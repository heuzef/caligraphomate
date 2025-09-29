#!/bin/bash
RUN="record-callibration-a5"
PUSH_TO_HUB="False"
EPISODE_TIME_S="60"
RESET_TIME_S="60"
NUM_EPISODES="1"
##############################

if [[ "$1" == "record" ]]; then
    rm -rfv ~/.cache/huggingface/lerobot/$HF_USER/$RUN/
    echo "Recording $RUN"
    python -m lerobot.record \
        --robot.type=so100_follower \
        --robot.port=$PORT_FOLLOWER \
        --robot.id=follower \
        --teleop.type=so100_leader \
        --teleop.port=$PORT_LEADER \
        --teleop.id=leader \
        --display_data=True \
        --dataset.push_to_hub=$PUSH_TO_HUB \
        --dataset.repo_id=$HF_USER/$RUN \
        --dataset.episode_time_s=$EPISODE_TIME_S \
        --dataset.reset_time_s=$RESET_TIME_S \
        --dataset.num_episodes=$NUM_EPISODES \
        --dataset.single_task="$RUN"

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