# AutoDash

[![Build Status](https://travis-ci.com/AutoDash/AutoDash.svg?branch=master)](https://travis-ci.com/AutoDash/AutoDash)

AutoDash is a semi-automated software pipeline for assembling collision and near-collision dashcam footage datasets. The goal of this pipeline is to provide a standard dataset for studies involving car collisions from an egocentric perspective.

# Requirements

You will need Python 3.7. It's also possible to use package binaries from our release builds.

In order to use most of the out-of-the-box configs, write access to our Firebase instance is required. Please contact us for more info.

# Dependencies

All Python dependencies can be found in [requirements.txt](./requirements.txt)

# Tests

You can run tests using the [run_tests.sh](./tools/run_tests.sh) script:

```bash
./tools/run_tests.sh
```

# Pipeline Configurations
All pipeline configurations can be found in the `custom_configs` folder.
To run a specific configuration, add the argument `--config <configuration_path>`. 

e.g. `./run --config custom_configs/smallcorgi_exporter.yml`

The following base configurations are specified:
| Configuration  | Description |
| --- | --- |
| backup_firebase_locally.yml  | Will copy the contents from the metadata storage in our Firebase instance so they can be modified locally. This is especially useful if you don't have write access to our Firebase instance but want to add your own videos.  |
| download_videos.yml  | This will download all videos that have been added to the database to your local machine.  |
| localstorage.yml  | Will run the pipeline using your own local storage for storing metadata, and doesn't rely on Firebase access.  |
| review_metadata_with_url.yml  | Allows you to review a specific video's metadata (specified as the url in the configuration file).  |
| review_processed_videos.yml  | Allows you to edit and update every video in the database that has been labeled with bounding boxes.  |
| review_unprocessed_videos.yml  | Allows you to edit and update every video in the database that has been NOT been labeled with bounding boxes.  |
| review_split_videos.yml  | Will run a configuration that downloads videos from the database that have been `split` but not `labelled` with bounding boxes (to be used in conjunction with `split_only_config.yml`). |
| smallcorgi_exporter.yml  | This will produce a folder with CSV files that contain all metadata of clips 5s in length.  |
| split_only_config.yml  | will run a configuration that downloads new videos from the Internet to be split into collision videos. |
# Installation

## User Setup

### Automatic Setup
We provide a script, `tools/setup.sh`, which automatically configures the pipeline for you. Simply clone the repo with `git clone https://github.com/AutoDash/AutoDash.git` and run the following:

```bash
./tools/setup.sh
```

### Manual Setup
If you encounter problems with automatic setup, the following steps may help you. First clone the repo as well as the submodules:

```bash
git clone https://github.com/AutoDash/AutoDash.git
cd AutoDash
git submodule update --init --recursive
```
Then install the required Python packages:
```bash
pip3 install -r requirements.txt
```
If the pip install fails, it may be becasue your version of pip is outdated, first try:
```bash
pip3 install --upgrade pip
```
to ensure newer versions of packages can be fetched by pip.

NOTE: we recommend using a Python [virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/) for installing the Python dependencies so that the packages don't conflict with any other Python projects.

## Developer Installation

### Required Software
First you must have the following required software:

- Python3.7 (with Pip)
- tkinter-py (install instructions can be [found here](https://tkdocs.com/tutorial/install.html))  
on Linux, can be installed with `sudo apt-get install python3-tk`

### Additional Software
For certain executors, additional software is required. Note that these are not required for the default configuration and only for some custom configurations.
- FFMPEG is only required for the SegmentSplitter(docs on how to install can be [found here](https://ffmpeg.org/download.html))  
On linux, ffmpeg can simply be installed with `sudo apt-get install ffmpeg`

# Usage
Once the pipeline has been setup, you can get started by running the local storage configuration (or any other configurations as described above):
```bash
./run --storage local --config custom_configs/localstorage.yml
```

With no options supplied, `./run` executes the default pipeline configuration which contains the following steps:
1. Fetches a video URL from our database of dashcam videos
2. Downloads the video to your local storage
3. Opens the labelling tool with the now edited video so you can label video information

## Labelling
The Labeler executor allows you to manually annotate a video with metadata fields that require human inspection to fill in. It first opens a new GUI window with a video player and begins accepting a combination of mouse and keyboard shortcuts as input.

An example of the GUI (in Selection mode) is shown below. There are 2 modes - Selection and Bounding Box mode - which will be elaborated on below. 
The logs on the right of the black region show a history of past actions, and will state which frames, indexes, and bounding boxes are impacted by previous commands. It may also offer suggestions and warnings depending on user activity. 
The left of the black region shows the current mode, along with mode-specific states. The information within will be elaborated on below.
The bounding boxes of objects are drawn, along with their object ids. If an object is marked as part of an accident, its bounding box will be shown in blue. If it isn’t, it will be shown in white.

The GUI in Selection mode. A blue bounding box means the object was involved in an accident.

**Trackbars**:
The 3 trackbars at the top are:
- Progress: Shows the current frame. The user can jump to any frame by clicking on the trackbar
- Frame delay: The number of milliseconds between frames, and corresponds to the frame rate. A lower frame delay results in a faster video
- Pause: Shows whether the video player is paused. The GUI continues to accept commands while the video is paused

**Labeller commands**
The GUI has be following general and navigation controls:
- `<H>`: Display the control mappings
- `<Esc>`: Abort all changes and restart
- `<Enter>`: Commit all changes, and exit
- `<Esc>`: Abort all changes and exit
- `<T>`: Open a separate window for attaching custom tags in the form of key-value pairs to the video, which can later be filtered or searched on
- `<W>, <S>, <A>, <D>`: Fine-grained navigation commands, for traversing the video frame by frame. They correspond to moving 10 frames forward, 10 frames back, 1 frame back, and 1   frame forward respectively. It is recommended to use these commands while the video is paused
- `<Space>`: Toggle pause
- `<Tab>`: Toggle between the 2 GUI modes, as elaborated below

**Selection Mode**:
In Selection mode, the GUI offers the general controls along with these additional controls:
- `<Left click>`: Click on an object’s bounding box to toggle whether it is part of collision or not. Objects selected as part of a collision will have a blue bounding box
- `<N>`: Toggle whether the video is taken from a dashcam. By default, videos are assumed to be dashcam videos. If a video is marked as not a dashcam video and the change is committed, it will not continue down the pipeline

**Bounding Box Mode**:
Bounding Box mode is for the manipulation of bounding boxes and object-specific properties. It offers the general controls along with these additional controls:
- `<Left click and drag>`: Draw a bounding box. This will be used as input for other commands. While drawing, the box currently being drawn will be shown in green.
- `<I>`: Open a separate window with 2 text inputs: object id and class. Any further changes in this mode will modify the selected object’s bounding boxes and properties
  If the id corresponds to an existing object, further commands will modify the existing object. The class of the object will not be overwritten with this command, but the logs   will display a warning if the input class is different from the original
  If the id does not exist, it will be added once its first bounding box is committed.
- `<U>`: Update the class of the currently selected object, overwriting it with the class input set by `<I>`
- `<R>`: Reset all bounding box inputs
- `<B>`: Commit a bounding box update, based on the last 2 bounding box inputs. The User should draw bounding boxes at the starting and ending frames, and then press b. The     bounding box will be automatically interpolated in between, so it is not necessary to draw every frame.
- `<C>`: Clear bounding boxes for the selected object with a range. The user should click on the starting and ending frames, and then press c.
- `<P>`: Prune all object ids that have no bounding boxes. This situation occurs when the user clears all bounding boxes for the given object.


The GUI in Bounding Box mode. The bounding box currently being drawn is in green

**GUI Mode Specific State Information**
In Selection mode, the information displayed is:
- Number of objects selected as a participant in a collision
- The total number of objects
- Whether this video is marked as a dashcam video

In Bounding Box mode, the information displayed is:
- The target object and class, as set by `<I>`. Whether this id corresponds to a existing or new object is also shown
- The frames of the last 2 drawn bounding box inputs. It will display only 1 if there is only 1 available, or so “No Input” if none is set
- If the mouse is currently clicking and dragging, the “Drawing from” and “Drawing to” selection shows coordinates of bounding box currently being drawn

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
