#!/bin/bash

BASEDIR=$(dirname "$0")
export PYTHONPATH="${PYTHONPATH}:${BASEDIR}/../src"
pytest -x -v
