#!/bin/bash

BASEDIR=$(dirname "$0")

# Setup anonymization submodule
git submodule update --init --recursive
cd "${BASEDIR}/../src/lib/anonymization" || exit
git checkout autodash
cd - || exit
cd "${BASEDIR}/.." || exit

# Install requirements
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# Install additional dependencies
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
    # Packages needed
    sudo apt update
    sudo apt install -y ffmpeg libmediainfo-dev python3-tk curl tar
elif [ "$(expr substr "$(uname -s)" 1 10)" == "MINGW32_NT" ]; then
    # Do something under 32 bits Windows NT platform
    echo "Windows unsupported"
elif [ "$(expr substr "$(uname -s)" 1 10)" == "MINGW64_NT" ]; then
    # Do something under 64 bits Windows NT platform
    echo "Windows unsupported"
fi

# Download model
if [[ -z "${CI}" ]] ; then
  mkdir "${BASEDIR}/../model"
  cd "${BASEDIR}/../model"
  curl -O http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_kitti_2018_01_28.tar.gz
  tar -xvf faster_rcnn_resnet101_kitti_2018_01_28.tar.gz
  rm faster_rcnn_resnet101_kitti_2018_01_28.tar.gz
fi 
