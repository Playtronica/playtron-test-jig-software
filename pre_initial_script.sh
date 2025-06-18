#!/bin/bash

REPO_NAME="playtron-test-jig-software"
REPO_SSH="git@github.com:Playtronica/playtron-test-jig-software.git"

ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1
ssh-keyscan github.com >> ~/.ssh/known_hosts

sudo cp -r .ssh /root
cat  ~/.ssh/id_rsa.pub
read -r -n 1 -p "Please enter this public ssh key to github repository. After press Enter" _

sudo apt update -y
sudo apt upgrade -y
sudo apt install -y git python3-pip


git clone ${REPO_SSH}

sudo cp ./${REPO_NAME}/initial_script.sh ./
sudo cp ./${REPO_NAME}/auto_update.service /etc/systemd/system
sudo cp ./${REPO_NAME}/start_jig.service /etc/systemd/system

sudo systemctl daemon-reload
sudo systemctl enable auto_update.service
sudo systemctl start auto_update.service