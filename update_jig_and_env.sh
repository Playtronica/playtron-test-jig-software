#!/bin/bash

git reset --hard
git pull
git checkout main

sudo pip install -r "requirements.txt" --break-system-packages


