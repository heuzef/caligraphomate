#!/bin/bash
RUN=$2
PUSH_TO_HUB="True"
EPISODE_TIME_S="15"
RESET_TIME_S="15"
NUM_EPISODES="5"
TASK="draw a circle"
##############################

if [[ "$1" == "record" ]]; then
    rm -rfv ~/.cache/huggingface/lerobot/$HF_USER/$RUN/
    echo "Recording $RUN"
    python -m lerobot.record \
        --robot.type=so100_follower \
        --robot.port=$PORT_FOLLOWER \
        --robot.id=follower \
        --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, top :{type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}}" \
        --teleop.type=so100_leader \
        --teleop.port=$PORT_LEADER \
        --teleop.id=leader \
        --display_data=True \
        --dataset.push_to_hub=$PUSH_TO_HUB \
        --dataset.repo_id=$HF_USER/$RUN \
        --dataset.episode_time_s=$EPISODE_TIME_S \
        --dataset.reset_time_s=$RESET_TIME_S \
        --dataset.num_episodes=$NUM_EPISODES \
        --dataset.single_task="$TASK"

elif [[ "$1" == "replay" ]]; then
    echo "Replaying $RUN"
    python -m lerobot.replay \
        --robot.type=so100_follower \
        --robot.port=$PORT_FOLLOWER \
        --robot.id=follower \
        --dataset.repo_id=$HF_USER/$RUN \
        --dataset.episode=0

else
    echo "Need arguments for $RUN"
    echo "record or replay"
fi