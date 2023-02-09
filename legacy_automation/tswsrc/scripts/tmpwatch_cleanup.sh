#!/bin/bash

###############################################################################
#temp watch
###############################################################################
# Remove files in the migt dir that have a creation older than -c hours

#MAILTO=splunkmail@splunk.research.sys
*/20 * * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 10 --exclude-pattern="/usr2/smartfilter/build/migt/ts/.ts_last_ran*"  /usr2/smartfilter/build/migt/ts
30 * * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 12 --exclude-pattern="/usr2/smartfilter/build/migt/xl/.xl_last_ran*" /usr2/smartfilter/build/migt/xl
 
# Remove URL files over 28 days old from archive directory
#MAILTO=splunkmail@splunk.research.sys
00 06,12,18 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 672 /usr2/smartfilter/build/archive/ts
35 06,12,18 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 672 /usr2/smartfilter/build/archive/xl
 
# Clean up sa_export dir, remove URL files over 30 days old
05 * * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 720 /usr2/smartfilter/build/sa_export
 
# Tmp watch the log files
#MAILTO=splunkmail@splunk.research.sys
00 00-19,23 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 168 /usr2/smartfilter/build/logs
15 12 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/master
 
# Tmp Watch the log files, remove files older than 15 days
30 12 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/migt/ts
00 13 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/migt/xl
 
# Tmp watch the log files
#MAILTO=splunkmail@splunk.research.sys
00 00-19,23 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 168 /usr2/smartfilter/build/logs
15 12 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/master
 
# Tmp Watch the log files, remove files older than 15 days
30 12 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/migt/ts
00 13 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/logs/migt/xl
 
# Tmp watch files, remove file older than 2 months
00 4,13 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 1440 /usr2/smartfilter/build/staging/ts
 
# Tmp watch files, remove file older than 3 months(28 days months)
15 4,13 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 2016 /usr2/smartfilter/build/staging/tsc
00 5,14 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 2016 /usr2/smartfilter/build/staging/xl
 
00 15 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 2016 /usr2/smartfilter/build/archive/xl
15 15 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 2016 /usr2/smartfilter/build/archive/ts
 
# Tmp watch on build files in hdfs_staging archive directory.
00 01-16 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 72 /hdfs_staging/archive/builds
 
# Tmp watch url publication history archive directory
00 06,18 * * * ulimit -s unlimited; /usr/sbin/tmpwatch -m 360 /usr2/smartfilter/build/publication_history/archive

