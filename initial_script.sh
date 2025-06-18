#!/bin/bash

REPO_NAME="playtron-test-jig-software"
REPO_SSH="git@github.com:Playtronica/playtron-test-jig-software.git"


if [ ! -d "${REPO_NAME}" ]; then
  git clone ${REPO_SSH}
fi

cd ${REPO_NAME} || exit

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate

git pull

pip install -r requirements.txt
python3 src/main.py