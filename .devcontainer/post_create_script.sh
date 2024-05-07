#!/bin/sh

# # List of environment variables
# env_vars=("EUL_REPO_USER" "EUL_REPO_PASSWORD" "EUL_ARESIS" )

# for var in "${env_vars[@]}"
# do
#   if [ -z "${!var}" ]; then
#     echo "Error ENV VAR : $var is not set or Empty "
#     exit 1
#   fi

#   echo "ENV VAR : $var is set to '${!var}'."
# done

# create the virtual env 
# export VENV_NAME=.venv
# export VENV_PATH=./$VENV_NAME
# python3 -m venv $VENV_NAME

# # activate venv 
# source "$VENV_PATH"/bin/activate

# Configure pip
pip config set global.index-url "https://pypi.org/simple/"


# # upgrade pip 
# "$VENV_PATH"/bin/python -m pip install --upgrade pip

# # install editable project with the dependencies listed in setup.py
# "$VENV_PATH"/bin/python -m pip install --no-cache-dir -e .[ci]

# # install and activate pre-commit
# "$VENV_PATH"/bin/python -m pip install pre-commit


# upgrade pip 
pip install --upgrade pip

# install editable project with the dependencies listed in setup.py
pip install --no-cache-dir -e .[ci]

# install and activate pre-commit
pip install pre-commit

pip install invoke 
pip install pip-tools

pre-commit install -f

invoke install