#!/bin/sh
export GHDATE=$(date -d "-5 minutes" -u +\%Y\%m\%d\%H\%M)
export COMMITDIR=/data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/commits
export WORKFLOWSOURCE=/data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/src
# Get GitHub Commits
python /home/toolguy/github_crawler/github_get_commits.py $GHDATE $COMMITDIR/$GHDATE.txt

# scrap urls
for i in $COMMITDIR/*.txt; 
do
    mv $i $i.scraping && 
    python /home/toolguy/github_crawler/github_scrape_commits.py $i.scraping $WORKFLOWSOURCE/$(basename $i) && 
    mv $i.scraping $i.scraped; 
done

