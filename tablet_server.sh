#!/usr/bin/env bash

INTERPRETER="/home/hdfs/miniconda3/bin/python"

source ~/.bashrc
#source ~/.bash_profile
cd `dirname $0`
${INTERPRETER} tablet_server.py 
