# Caligraphomate
(C) Heuzef.com - 2025

Use SO-ARM like an Handwriting Machines !

## Étymologie
> Cali- : Du grec kállos, signifiant "beauté". Cela ancre immédiatement le mot dans la qualité esthétique que l'on retrouve en calligraphie.

> Grapho- : Du grec gráphein, signifiant "écrire" ou "dessiner". Cela désigne l'acte de créer du texte ou des images.

> -Mate : Ce suffixe implique souvent une machine, un automate, ou quelque chose qui exécute une fonction automatiquement. Il établit un lien clair avec l'aspect "machine" (du grec mêkhanê) de "mécanique" et la nature automatisée suggérée par "robot" (effectuant la robota, "corvée" ou "travail").

## Ressources
* https://calligrapher.ai
* https://axidraw.com
* "Handwriting Machines" / "Autopen"

## Quickstart whith LeRobot
```bash
git clone https://github.com/huggingface/lerobot.git ; cd lerobot
docker build -f docker/Dockerfile.user -t lerobot-user .
docker run -it --device=/dev/ -v /dev/:/dev/ --rm lerobot-user
# Inside the container
uv pip install --no-cache ".[feetech]"
```

> Then, configure the motors : https://huggingface.co/docs/lerobot/so101?example=Linux#configure-the-motors

> Play : https://huggingface.co/docs/lerobot/getting_started_real_world_robot