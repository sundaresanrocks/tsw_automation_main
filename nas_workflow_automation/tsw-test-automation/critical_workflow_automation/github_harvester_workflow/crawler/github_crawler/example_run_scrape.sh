#!/bin/sh
for FILE in ./*.txt; do
   python github_scrape_commits.py ${FILE} ${FILE}_exes && mv ${FILE} ${FILE}_scraped
done
