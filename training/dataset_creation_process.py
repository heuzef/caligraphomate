#!/usr/bin/env python3
import os
import subprocess
import sys
import termios
import tty
from static_camera import StaticImageCamera

# === CONFIGURATION ===
SVG_ROOT = "../svg/selected_svg"
PNG_ROOT = "../png"
HF_USER = "Heuzef"
PORT_LEADER = "/dev/ttyACM0"
PORT_FOLLOWER = "/dev/ttyACM1"
EPISODE_TIME_SEC = 60
RESET_TIME_SEC = 10
TASK_DESCRIPTION = "Draw the image"
PUSH_TO_HUB = True


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


def record_single_episode(dataset, shape, episode_id, total_episodes, png_path, push=False):
    """Lance un enregistrement pour un épisode unique."""
    print(f" {shape} | Épisode {episode_id + 1}/{total_episodes}")
    print(f"  Image targer : {png_path}")

    camera_config = {
        "front": OpenCVCameraConfig(index_or_path="/dev/video0", width=640, height=480, fps=FPS),
        "top": OpenCVCameraConfig(index_or_path="/dev/video2", width=640, height=480, fps=FPS),
        "target": StaticImageCamera(index_or_path=png_path, width=640, height=480, fps=FPS)
    }
    robot_config = SO100FollowerConfig(
        port=PORT_FOLLOWER, id="my_awesome_follower_arm", cameras=camera_config
    )
    teleop_config = SO100LeaderConfig(port=PORT_LEADER, id="my_awesome_leader_arm")

# Initialize the robot and teleoperator
    robot = SO100Follower(robot_config)
    teleop = SO100Leader(teleop_config)

# Configure the dataset features
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

# Initialize the keyboard listener and rerun visualization
    _, events = init_keyboard_listener()
    init_rerun(session_name="recording")

# Connect the robot and teleoperator
    robot.connect()
    teleop.connect()

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
    if not events["stop_recording"] and (episode_idx < NUM_EPISODES - 1 or events["rerecord_episode"]):
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
    robot.disconnect()
    teleop.disconnect()
    if push:
        dataset.push_to_hub()

    print("RUNNING IN SUBPROCESS")
    subprocess.run(command, check=True)
    print("RAN IN SUBPROCESS")
    print(f" Épisode {episode_id + 1}/{total_episodes} terminé.\n")


def record_shape(shape):
    """Crée un dataset Hugging Face pour une forme donnée."""
    svg_dir = os.path.join(SVG_ROOT, shape)
    png_dir = os.path.join(PNG_ROOT, shape)
    if not os.path.isdir(svg_dir) or not os.path.isdir(png_dir):
        print(f"  Forme '{shape}' introuvable dans svg/ ou png/.")
        return

    svg_files = sorted(f for f in os.listdir(svg_dir) if f.endswith(".svg"))
    total = len(svg_files)
    if total == 0:
        print(f"  Aucun fichier SVG trouvé pour {shape}")
        return

    # ==================== ATTENTION =======================
    total=5

    print(f"\n===  Création du dataset '{shape}' ({total} épisodes) ===")

    # Create the dataset
    dataset = LeRobotDataset.create(
        repo_id=f"{HF_USER}/{shape}",
        fps=FPS,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4,
    )

    for i, svg_file in enumerate(svg_files):
        png_file = os.path.splitext(svg_file)[0] + ".png"
        png_path = os.path.join(png_dir, png_file)

        if not os.path.exists(png_path):
            print(f" PNG manquant pour {svg_file}, saut de cet épisode.")
            continue

        # Détermine si on push à la fin de l'épisode
        push = (i == total - 1)

        record_single_episode(dataset, shape, i, total, png_path, push=push) # TO UNCOMMENT

        if i < total - 1:
            action = wait_for_space_or_enter()
            if action == "push_quit":
                # push dataset actuel
                record_single_episode(shape, i, total, png_path, push=True) # TO UNCOMMENT
                return "quit"

    print(f"🚀 Dataset '{shape}' poussé sur Hugging Face !\n")
    return "continue"


def main():
    try:
        shapes = sorted(os.listdir(SVG_ROOT))
        for shape in shapes:
            result = record_shape(shape)
            if result == "quit":
                break
    except KeyboardInterrupt:
        print("\n Script interrompu par l'utilisateur. Arrêt propre.")


if __name__ == "__main__":
    main()
