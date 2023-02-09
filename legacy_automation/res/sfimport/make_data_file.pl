#!/usr/bin/perl

@cats = ('bu', 'ms');
@harvester = ('WWUncat', 'Customer');

$counter=0;
foreach $cat (@cats) {
  foreach $harvester (@harvester) {
    $counter++;
    print qq($counter,sfimporttestdomain$counter.com,"-a 81 -H ""$harvester"" -f u -D -A -c $cat",Total_Successful=0;Total_Errors=0;Total_Canon_Errors=0\n);
  }
}
