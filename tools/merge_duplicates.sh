#!/bin/bash

BASEDIR=$(dirname "$0")
export PYTHONPATH="${PYTHONPATH}:${BASEDIR}/../src"
$BASEDIR/merge_duplicates.py
