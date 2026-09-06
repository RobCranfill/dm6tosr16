#!/bin/bash
# install the service that will run the DM6toSR16 app at startup

sudo cp dm6tosr16.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/dm6tosr16.service
sudo systemctl enable dm6tosr16.service