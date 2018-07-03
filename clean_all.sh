#!/bin/bash
#clean_all.sh
rm -rf ./capture ./__pycache__/ ./*~ ./log.txt
rm -rf ./Lib/__pycache__/ ./Lib/*~
cd ./Tools;./clean_all.sh;cd ../
