#!/usr/bin/env python3
import os
import subprocess
import sys
import termios
import tty
from pathlib import Path
from static_image_camera import StaticImageCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from static_image_camera_config import StaticImageCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.robots.so100_follower import SO100Follower, SO100FollowerConfig
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun as init_rerun
from lerobot.record import record_loop

# === CONFIGURATION ===
JPG_ROOT = "../jpg"
HF_USER = "Heuzef"
HF_MODEL_ID = f"{HF_USER}/act_rectangle_v2"
#HF_MODEL_ID = f"lerobot/act_aloha_sim_transfer_cube_human"
PORT_LEADER = "/dev/ttyACM0"
PORT_FOLLOWER = "/dev/ttyACM1"
EPISODE_TIME_SEC = 30
RESET_TIME_SEC = 0
TASK_DESCRIPTION = "Draw the image"
FPS=30


def wait_for_space_or_enter():
    """
    Attend que l'utilisateur appuie sur :
    - Espace : passer au prochain épisode
    - Entrée : push et quitter le script
    """
    print("\n  [ESPACE] : épisode suivant | [ENTRÉE] : quitter")
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == " ":
                print("  Épisode suivant...\n")
                return "next"
            elif ch == "\r" or ch == "\n":
                print(" Sortie du script...\n")
                return "quit"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def infer_one_episode(dataset, episode_id, total_episodes, robot, policy):
    print(f" Épisode {episode_id + 1}/{total_episodes}")

# Initialize the keyboard listener and rerun visualization
    _, events = init_keyboard_listener()
    init_rerun(session_name="recording")

    print(f"Infer episode {episode_id + 1} of {total_episodes}")

#   preprocessor, postprocessor = make_pre_post_processors(
#       policy_cfg=policy,
#       pretrained_path=HF_MODEL_ID,
#       dataset_stats=dataset.meta.stats,
#   )

    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        policy=policy,
#       preprocessor=preprocessor,
#       postprocessor=postprocessor,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=True
    )

    print(f" Épisode {episode_id + 1}/{total_episodes} terminé.\n")


def infer(jpg_files):
    """Crée un dataset Hugging Face pour une forme donnée."""
    camera_config = {
        "front": OpenCVCameraConfig(index_or_path="/dev/video0", width=640, height=480, fps=FPS),
        "top": OpenCVCameraConfig(index_or_path="/dev/video2", width=640, height=480, fps=FPS)
    }
    robot_config = SO100FollowerConfig(
        port=PORT_FOLLOWER, id="follower", cameras=camera_config
    )
    robot = SO100Follower(robot_config)
    static_image_conf = StaticImageCameraConfig(path=None, width=640, height=480, fps=FPS)
    robot_config.cameras["target"] = static_image_conf
    robot.cameras["target"] = StaticImageCamera(static_image_conf)

    policy = ACTPolicy.from_pretrained(HF_MODEL_ID)

    # Configure the dataset features
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

    # Create the dataset
    dataset = LeRobotDataset.create(
        repo_id=f"{HF_USER}/eval_v1",
        fps=FPS,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4
    )

    # ==================== ATTENTION =======================
    total=len(jpg_files)

    for i, jpg_file in enumerate(jpg_files):
        if not os.path.exists(jpg_file):
            print(f"  Fichier '{jpg_file}' introuvable.")
            continue

        print(f"\n\nFor loop iteration {i} file {jpg_file}")
        print(f"START")
        action = wait_for_space_or_enter()
        if action == "quit":
            return "quit"

        print(f"  Image target : {jpg_file}")
        static_image_conf.path = jpg_file

        robot.connect()

        infer_one_episode(dataset, i, total, robot, policy) # TO UNCOMMENT

        robot.disconnect()

    return "continue"


def main():
    try:
        jpg_files = [f"{JPG_ROOT}/rectangle/rectangle_060.jpg"]
        result = infer(jpg_files)
    except KeyboardInterrupt:
        print("\n Script interrompu par l'utilisateur. Arrêt propre.")


if __name__ == "__main__":
    main()
