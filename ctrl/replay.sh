python -m lerobot.replay \
    --robot.type=so100_follower \
    --robot.port={$PORT_FOLLOWER} \
    --robot.id=follower \
    --dataset.repo_id={$HF_USER}/record-test \
    --dataset.episode=0