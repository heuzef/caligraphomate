#!/bin/bash

PNG_ROOT="png"
OUTPUT_ROOT="videos"
WIDTH=640
HEIGHT=480
FPS=30
DURATION=15

mkdir -p "$OUTPUT_ROOT"

for shape in "$PNG_ROOT"/*; do
    [ -d "$shape" ] || continue
    shape_name=$(basename "$shape")
    mkdir -p "$OUTPUT_ROOT/$shape_name"

    for png in "$shape"/*.png; do
        [ -f "$png" ] || continue
        base=$(basename "$png" .png)
        out="$OUTPUT_ROOT/$shape_name/$base.mp4"
        ffmpeg -y -loop 1 -i "$png" \
        -f lavfi -i color=c=white:s=${WIDTH}x${HEIGHT} \
        -filter_complex "[0]scale='if(gt(a,${WIDTH}/${HEIGHT}),${WIDTH},-1)':'if(gt(a,${WIDTH}/${HEIGHT}),-1,${HEIGHT})'[fg];[1][fg]overlay=(W-w)/2:(H-h)/2:format=auto" \
        -t $DURATION -r $FPS "$out"
        echo "✅ Créé : $out"
    done
done
