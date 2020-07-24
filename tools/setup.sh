#!/bin/bash

BASEDIR=$(dirname "$0")

# setup anonymization submodule
git submodule update --init --recursive
cd "${BASEDIR}/../src/lib/anonymization" || exit
git checkout autodash
cd - || exit
cd "${BASEDIR}/.." || exit

# install requirements
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# install additional dependencies
if [ "$(uname)" == "Darwin" ]; then
    # Platform is Mac OS X
    brew update
    brew install ffmpeg
    brew install mediainfo
elif [ "$(expr substr "$(uname -s)" 1 5)" == "Linux" ]; then
    # Platform is GNU/Linux
    distro_ver=$(expr substr "$(lsb_release -c)" 10 11 | sed -e 's/^[[:space:]]*//')
    if [ "$distro_ver" == "xenial" ]; then
      # Ubuntu distro version is xenial
      sudo add-apt-repository -y ppa:mc3man/xerus-media
    elif [ "$distro_ver" == "bionic" ]; then
      # Ubuntu distro version is bionic
      sudo add-apt-repository -y ppa:mc3man/bionic-media
    elif [ "$distro_ver" == "trusty" ]; then
      # Ubuntu distro version is trusty
      sudo add-apt-repository -y ppa:mc3man/trusty-media
    fi
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    sudo apt-get install -y libmediainfo-dev
elif [ "$(expr substr "$(uname -s)" 1 10)" == "MINGW32_NT" ]; then
    # Do something under 32 bits Windows NT platform
    echo "Windows unsupported"
elif [ "$(expr substr "$(uname -s)" 1 10)" == "MINGW64_NT" ]; then
    # Do something under 64 bits Windows NT platform
    echo "Windows unsupported"
fi
