#!/bin/bash

REPO_NAME="playtron-test-jig-software"
REPO_SSH="git@github.com:Playtronica/playtron-test-jig-software.git"

ssh-keygen -q -o -t rsa -N '' -C “ssh@github.com” -f /root/.ssh/id_rsa <<<y >/dev/null 2>&1
ssh-keyscan github.com >> /root/.ssh/known_hosts

cat  /root/.ssh/id_rsa.pub
read -r -n 1 -p "Please enter this public ssh key to github repository. After press Enter" _

sudo apt update -y
sudo apt upgrade -y
sudo apt install -y git python3-pip libjack-jackd2-dev

git clone ${REPO_SSH}

sudo cp /root/${REPO_NAME}/start_jig.sh ./
sudo cp /root/${REPO_NAME}/update_jig_and_env.sh ./
sudo cp /root/${REPO_NAME}/start_jig.service /etc/systemd/system
sudo cp /root/${REPO_NAME}/update_jig_and_env.service /etc/systemd/system

sudo systemctl daemon-reload
sudo raspi-config nonint do_i2c 0

sudo systemctl enable update_jig_and_env.service
sudo systemctl start update_jig_and_env.service
sudo systemctl enable start_jig.service
sudo systemctl start start_jig.service