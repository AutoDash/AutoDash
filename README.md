# AutoDash

[![Build Status](https://travis-ci.com/AutoDash/AutoDash.svg?branch=master)](https://travis-ci.com/AutoDash/AutoDash)

AutoDash is a pipeline aggregating dashcam footage for (near-)collision incidents. The goal of this pipeline is to provide a standard dataset for studies involving car collisions from an egocentric perspective.

# Requirements

You will need Python 3.7. It's also possible to use package binaries from our release builds.

# Dependencies

All dependencies can be found in [requirements.txt](./requirements.txt)

# Tests

You can run tests using the [run_tests.sh](./tools/run_tests.sh) file

# Pipeline Configurations

If you run the pipeline with the arg `--config custom_configs/smallcorgi_exporter.yml` then it will produce a folder with csv files that contain all completed metadatas

# Installation

## Developer Installation
First you must have the following required software:

- Python3.7 (with Pip)
- tkinter-py (docs on how to install can be [found here](https://tkdocs.com/tutorial/install.html))
- ffmpeg (docs on how to install can be [found here](https://ffmpeg.org/download.html))

Then we begin the setup:
Clone The repo as well as the submodules:

```bash
git clone https://github.com/AutoDash/AutoDash.git
cd AutoDash
git submodule update --init --recursive
```
Then install the required python packages
```bash
pip install -r requirements.txt
```
Note we recommend using a python [virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/) for installing the python code

Now you can run the readonly configuration:
```bash
./run --storage local --config custom_configs/readonly_configuration.yml
```