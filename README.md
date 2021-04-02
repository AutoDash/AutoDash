# AutoDash

[![Build Status](https://travis-ci.com/AutoDash/AutoDash.svg?branch=master)](https://travis-ci.com/AutoDash/AutoDash)

AutoDash is a pipeline aggregating dashcam footage for (near-)collision incidents. The goal of this pipeline is to provide a standard dataset for studies involving car collisions from an egocentric perspective.

# Requirements

You will need Python 3.7. It's also possible to use package binaries from our release builds.

In order to use most of the out of the box configs, write access to the AutoDash firebase is required. Please contact us for more info.

# Dependencies

All dependencies can be found in [requirements.txt](./requirements.txt)

# Tests

You can run tests using the [run_tests.sh](./tools/run_tests.sh) file

# Pipeline Configurations
All pipeline configurations can be found in the `custom_configs` folder.
To run a specific configuration, add the argument `--config <configuration_path>` 

e.g. `./run --config custom_configs/smallcorgi_exporter.yml`

The following base configurations are specified
| Configuration  | Description |
| --- | --- |
| backup_firebase_locally.yml  | Will copy the contents from the metadata storage in firebase so they can be modified locally. This is especially useful if you don't have write access to the firebase but want to add your own videos  |
| download_videos.yml  | This will download all videos that have been added to the database to your local machine  |
| review_metadata_with_url.yml  | allows you to review a specific video's metadata (specified as the url in the configuration file)  |
| review_processed_videos.yml  | Allows you to edit and update every video in the database that has been labeled with bounding boxes  |
| review_unprocessed_videos.yml  | Allows you to edit and update every video in the database that has been NOT been labeled with bounding boxes  |
| review_split_videos.yml  | will run a configuration that downloads videos from the database that have been `split` but not `labelled` with bounding boxes (to be used in conjunction with `split_only_config.yml`) |
| smallcorgi_exporter.yml  | will produce a folder with csv files that contain all metadatas with 5s clips of collisions  |
| split_only_config.yml  | will run a configuration that downloads new videos from the internet to be split into collision videos |
# Installation

## Developer Installation

### Required Software
First you must have the following required software:

- Python3.7 (with Pip)
- tkinter-py (genral docs on how to install can be [found here](https://tkdocs.com/tutorial/install.html))  
for Linux, can be installed with `sudo apt-get install python3-tk`

### Additional Software
For certain executors, additional software is required. Note that these are more unique use cases and don't have to be installed for the default configuration.
- ffmpeg is only required for the SegmentSplitter(docs on how to install can be [found here](https://ffmpeg.org/download.html))  
On linux, ffmpeg can simply be installed with `sudo apt-get install ffmpeg`

### Setup
To start seup, clone The repo as well as the submodules:

```bash
git clone https://github.com/AutoDash/AutoDash.git
cd AutoDash
git submodule update --init --recursive
```
Then install the required python packages
```bash
pip3 install -r requirements.txt
```
If the pip install fails, it may be becasue your version of pip is outdated, first try
```bash
pip3 install --upgrade pip
```
to ensure newer versions of packages can be fetched by pip.

NOTE: we recommend using a python [virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/) for installing the python code so the packages don't conflict with any other python projects


Now you can run the readonly configuration:
```bash
./run --storage local --config custom_configs/review_processed_videos_readonly.yml
```
This will go though the database, and display in the GUI any video that has been processed.

# Troubleshooting
## Runtime Errors
   - If you encounter an exception `google.auth.exceptions.RefreshError` with the payload
   ```json
   {
      "error": "invalid_grant",
      "error_description": "Invalid JWT: Token must be a short-lived token (60 minutes) and in a reasonable timeframe. Check your iat and exp values and use a clock with skew to account for clock differences between systems."
   }
   ```
   this most likely means that the clock time on your system is out of sync. You must synchronize your clock with the Internet using a server such as `time.nist.gov`. On Ubuntu, this can be accomplished by installing `ntpdate` and running `sudo ntpdate time.nist.gov`.
