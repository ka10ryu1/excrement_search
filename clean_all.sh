#!/bin/bash
#clean_all.sh
rm -rf ./capture ./__pycache__/ ./*~ ./log.txt
cd ./Tools;./clean_all.sh;cd ../
