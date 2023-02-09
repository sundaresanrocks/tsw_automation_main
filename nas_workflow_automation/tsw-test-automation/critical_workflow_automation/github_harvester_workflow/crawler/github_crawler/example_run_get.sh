#!/bin/sh
export CUR_DATE=$(date -d "-5 minutes" -u +\%Y\%m\%d\%H\%M)
python github_get_commits.py $CUR_DATE ./$CUR_DATE.txt
