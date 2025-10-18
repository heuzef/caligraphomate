#!/usr/bin/env python3
import os
import subprocess
import sys
import termios
import tty

# === CONFIGURATION ===
SVG_ROOT = "svg/selected_svg"
PNG_ROOT = "png"
HF_USER = "Heuzef"
PORT_LEADER = "/dev/ttyACM0"
PORT_FOLLOWER = "/dev/ttyACM1"
EPISODE_TIME_S = 15
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


def record_single_episode(shape, episode_id, total_episodes, png_path):
    """Lance un enregistrement pour un épisode unique."""
    print(f" {shape} | Épisode {episode_id + 1}/{total_episodes}")
    print(f" Image Target: {png_path}")

    # Définition des caméras
    cameras_arg = (
        "{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, "
        "top :{type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}, "
        f"target: {{type: image, index_or_path: {os.path.abspath(png_path)}}} }}"
    )

    # Commande d'enregistrement
    command = [
        "python", "-m", "lerobot.record",
        "--robot.type=so100_follower",
        f"--robot.port={PORT_FOLLOWER}",
        "--robot.id=follower",
        f"--robot.cameras={cameras_arg}",
        "--teleop.type=so100_leader",
        f"--teleop.port={PORT_LEADER}",
        "--teleop.id=leader",
        "--display_data=True",
        f"--dataset.repo_id={HF_USER}/{shape}",
        f"--dataset.episode_time_s={EPISODE_TIME_S}",
        "--dataset.reset_time_s=0",
        "--dataset.num_episodes=1",
        f"--dataset.single_task={shape}",
        f"--dataset.push_to_hub={PUSH_TO_HUB if episode_id + 1 == total_episodes else False}",
        f"--dataset.local_dir=./local_datasets/{shape}"
    ]

    subprocess.run(command, check=True)
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

    for i, svg_file in enumerate(svg_files):
        png_file = os.path.splitext(svg_file)[0] + ".png"
        png_path = os.path.join(png_dir, png_file)

        if not os.path.exists(png_path):
            print(f" PNG manquant pour {svg_file}, saut de cet épisode.")
            continue

        # Détermine si on push à la fin de l'épisode
        push = (i == total - 1)

        record_single_episode(shape, i, total, png_path, push=push) # TO UNCOMMENT

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