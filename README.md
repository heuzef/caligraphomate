<p>
  <img alt="LeRobot, Hugging Face Robotics Library" src="./caligraphomate.png" width="20%">
  <br/>
  <br/>
</p>

# Caligraphomate
(C) Heuzef.com - 2025

Use SO-ARM like an Handwriting Machines !

## Étymologie
> Cali- : Du grec kállos, signifiant "beauté". Cela ancre immédiatement le mot dans la qualité esthétique que l'on retrouve en calligraphie.

> Grapho- : Du grec gráphein, signifiant "écrire" ou "dessiner". Cela désigne l'acte de créer du texte ou des images.

> -Mate : Ce suffixe implique souvent une machine, un automate, ou quelque chose qui exécute une fonction automatiquement. Il établit un lien clair avec l'aspect "machine" (du grec mêkhanê) de "mécanique" et la nature automatisée suggérée par "robot" (effectuant la robota, "corvée" ou "travail").

## Quickstart whith LeRobot on Ubuntu

```bash
sudo ufw disable
sudo apt update ; sudo apt upgrade
sudo apt-get install -y python3-full ffmpeg cmake build-essential pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev pkg-config python-is-python3 curl inkscape

git clone https://github.com/huggingface/lerobot.git
cd lerobot

python -m venv .venv
source .venv/bin/activate

pip install -e .
pip install ".[aloha,feetech]"
```

## Setup Caligraphomate

```bash
sudo echo HUGGINGFACE_TOKEN=********** >> /etc/environment
git config --global credential.helper store
hf auth login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential
git clone git@github.com:heuzef/caligraphomate.git
cd caligraphomate
sudo sh env.sh
cp -vr huggingface ~/.cache/
```

> Then, configure the motors : https://huggingface.co/docs/lerobot/so101?example=Linux#configure-the-motors

# Actions control

```bash
# Locate USB ports
python -m lerobot.find_port
sh permissions.sh

# Setup motors
python -m lerobot.setup_motors --robot.type=so100_follower --robot.port=$PORT_FOLLOWER
python -m lerobot.setup_motors --teleop.type=so100_leader --teleop.port=$PORT_LEADER

# Calibrate
python -m lerobot.calibrate --robot.type=so100_follower --robot.port=$PORT_FOLLOWER --robot.id=follower
python -m lerobot.calibrate --teleop.type=so100_leader --teleop.port=$PORT_LEADER --teleop.id=leader

# Teleoperate
python -m lerobot.teleoperate --robot.type=so100_follower --robot.port=$PORT_FOLLOWER --robot.id=follower --robot.cameras="{ front: {type: opencv, index_or_path: 2, width: 1280, height: 720, fps: 30}}" --teleop.type=so100_leader --teleop.port=$PORT_LEADER --teleop.id=leader
```

> Play : https://huggingface.co/docs/lerobot/getting_started_real_world_robot

# Drive Caligraphomate

```bash
cd ~/GIT/caligraphomate
source ~/GIT/lerobot/.venv/bin/activate
sh permissions.sh
cat /etc/environment
./ctrl/teleoperate.sh 
```

# Phosphobot

> Open source service for full web control the Arm La documentatin est accessible ici : https://docs.phospho.ai/welcome

## Setup

```bash
curl -fsSL https://raw.githubusercontent.com/phospho-app/phosphobot/main/install.sh | sudo bash
sudo apt update && sudo apt install --only-upgrade phosphobot # For update
```

## Run
```bash
phosphobot run
```
> Run on http://localhost:8020

## Service (autostart at boot)

```bash
sudo cp phosphobot.service /etc/systemd/system/phosphobot.service
sudo systemctl daemon-reload
sudo systemctl enable phosphobot.service
sudo systemctl start phosphobot.service
sudo systemctl status phosphobot.service
sudo journalctl -u phosphobot.service -f
```

## Remote control with SSH tunnel
```bash
ssh -p 2233 -L 8020:localhost:8020 heuzef@heuzef.com -N
```