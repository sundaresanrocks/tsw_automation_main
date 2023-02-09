#!/bin/sh
# Copy data from /data/urldb to a backup locaiton
cp -R /data/urldb/* /data/webcache/backup_urldb_json

#Running the loader workflow
`/opt/sftools/bin/StartWorkflow.sh /opt/sftools/conf/urldbqueueloader.properties`
