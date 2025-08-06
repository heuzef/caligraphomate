cd ~/GIT/caligraphomate
source ~/GIT/lerobot/.venv/bin/activate
sudo chmod 666 /dev/ttyACM0
sudo chmod 666 /dev/ttyACM1
cat /etc/environment
echo "Check USB port with python -m lerobot.find_port"