# Github Harvester Workflow
This workflow has two docker containers that include 1) github-crawler and 2) github-workflow. 

# github-crawler
This container is to download .exes from the github commits. It saves the urls in crawler/download/ directory.
# github-workflow
This container runs the GithubHarvesterWorkflow and it reads the dowloaded files from github-crawler.
# Details
https://confluence-lvs.prod.mcafee.com/display/WSR/%5BTSWPLATT-326%5D+Test+automation+for+Github+workflow
