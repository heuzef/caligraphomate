#!/usr/bin/env python3
import os
import subprocess
import sys
import termios
import tty
from static_image_camera import StaticImageCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from static_image_camera_config import StaticImageCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.robots.so100_follower import SO100Follower, SO100FollowerConfig
from lerobot.teleoperators.so100_leader.config_so100_leader import SO100LeaderConfig
from lerobot.teleoperators.so100_leader.so100_leader import SO100Leader
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun as init_rerun
from lerobot.record import record_loop

# === CONFIGURATION ===
JPG_ROOT = "../jpg"
HF_USER = "Heuzef"
PORT_LEADER = "/dev/ttyACM0"
PORT_FOLLOWER = "/dev/ttyACM1"
EPISODE_TIME_SEC = 10
RESET_TIME_SEC = 0
TASK_DESCRIPTION = "Draw the image"
FPS=30


def wait_for_space_or_enter():
    """
    Attend que l'utilisateur appuie sur :
    - Espace : passer au prochain épisode
    - Entrée : push et quitter le script
    """
    print("\n  [ESPACE] : épisode suivant | [ENTRÉE] : push et quitter")
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
                print(" Push et sortie du script...\n")
                return "push_quit"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def record_single_episode(dataset, shape, episode_id, total_episodes,
                          robot, teleop):
    """Lance un enregistrement pour un épisode unique."""
    print(f" {shape} | Épisode {episode_id + 1}/{total_episodes}")

# Initialize the keyboard listener and rerun visualization
    _, events = init_keyboard_listener()
    init_rerun(session_name="recording")

    log_say(f"Recording episode {episode_id + 1} of {total_episodes}")

    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        teleop=teleop,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=True,
    )

    # Reset the environment if not stopping or re-recording
    if not events["stop_recording"] and (episode_id < total_episodes - 1 or events["rerecord_episode"]):
        log_say("Reset the environment")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop=teleop,
            control_time_s=RESET_TIME_SEC,
            single_task=TASK_DESCRIPTION,
            display_data=True,
        )

    if events["rerecord_episode"]:
        log_say("Re-recording episode")
        events["rerecord_episode"] = False
        events["exit_early"] = False
        dataset.clear_episode_buffer()
        return

    dataset.save_episode()

# Clean up
    log_say("Stop recording")

    print(f" Épisode {episode_id + 1}/{total_episodes} terminé.\n")


def record_shape(shape):
    """Crée un dataset Hugging Face pour une forme donnée."""
    jpg_dir = os.path.join(JPG_ROOT, shape)
    if not os.path.isdir(jpg_dir):
        print(f"  Forme '{shape}' introuvable dans jpg.")
        return

    jpg_dir = sorted(f for f in os.listdir(jpg_dir) if f.endswith(".jpg"))
    total = len(jpg_dir)
    if total == 0:
        print(f"  Aucun fichier JPG trouvé pour {shape}")
        return

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

    teleop_config = SO100LeaderConfig(port=PORT_LEADER, id="leader")

    teleop = SO100Leader(teleop_config)

    # Configure the dataset features
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

    # Create the dataset
    dataset = LeRobotDataset.create(
        repo_id=f"{HF_USER}/{shape}_v1",
        fps=FPS,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4
    )

    # ==================== ATTENTION =======================
    # total=10

    print(f"\n===  Création du dataset '{shape}' ({total} épisodes) ===")

    for i, jpg_file in enumerate(jpg_dir):
        print(f"\n\nFor loop iteration {i} file {jpg_file}")
        print(f"START")
        action = wait_for_space_or_enter()
        if action == "push_quit":
            dataset.push_to_hub()
            return "quit"
        jpg_path = os.path.join(jpg_dir, jpg_file)

        if not os.path.exists(jpg):
            print(f" JPG manquant pour {jpg_file}, saut de cet épisode.")
            continue

        print(f"  Image targer : {jpg_path}")
        static_image_conf.path = jpg_path

        # Détermine si on push à la fin de l'épisode
        push = (i == total - 1)

        # Connect the robot and teleoperator
        robot.connect()
        teleop.connect()

        record_single_episode(dataset, shape, i, total, robot, teleop) # TO UNCOMMENT

        robot.disconnect()
        teleop.disconnect()

        if push:
            dataset.push_to_hub()

    print(f"🚀 Dataset '{shape}' poussé sur Hugging Face !\n")
    return "continue"


def main():
    try:
        shapes = sorted(s for s in os.listdir(SVG_ROOT) if s in ["polygon"])  # WARNING circle DIRTY AF
        for shape in shapes:
            result = record_shape(shape)
            if result == "quit":
                break
    except KeyboardInterrupt:
        print("\n Script interrompu par l'utilisateur. Arrêt propre.")


if __name__ == "__main__":
    main()
