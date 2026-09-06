#!/bin/bash
# command-line helper to start/stop/whatever the dm6tosr16 service

sudo systemctl $1 dm6tosr16.service
