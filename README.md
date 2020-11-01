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