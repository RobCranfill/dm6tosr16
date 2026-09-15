#!/bin/bash
echo pulling files from PiFlight via SMB...

FILES="README.md
dm6tosr16_gui_pil.py
dm6tosr16_gui_pg.py
requirements.text
dm6tosr16.service
dm6tosr16_service.sh
install_service.sh
connect_dm6tosr16.sh"

for f in $FILES
do
  scp piflight.local:/home/rob/proj/dm6tosr16/$f .
done

git status

