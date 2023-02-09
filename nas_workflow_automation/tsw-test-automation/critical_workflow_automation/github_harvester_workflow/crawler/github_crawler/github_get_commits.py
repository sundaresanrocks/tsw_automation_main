import urllib2
import time
import datetime
import re
import os
import ujson
import wsr_logger
import sys

logger = wsr_logger.get_logger("python.github_commit_search")


def get_next_pages(links_header):
    # Format is like this: < Link: <https://....&page=2>; rel="next", <https://...&page=34>; rel="last"
    m = re.search('.*<(.*)>.*<(.*)>', links_header)
    link_raw = m.group(1)[:-1]
    next_page = int(m.group(1).split("=")[-1])
    last_page = int(m.group(2).split("=")[-1])
    logger.debug("next_page=%d, last_page=%d" % (next_page, last_page))

    return [link_raw + str(i) for i in xrange(next_page, last_page + 1)]


def download_api_url(url):
    logger.info("Downloading search_url=%s" % url)
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/vnd.github.cloak-preview')
    resp = urllib2.urlopen(req)
    tries_left = int(resp.info().getheader('X-RateLimit-Remaining'))
    tries_renewal = int(resp.info().getheader('X-RateLimit-Reset'))
    seconds_to_wait = 0
    if tries_left <= 0:
        utc_delta = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1))
        utc_secs_now = utc_delta.days * 24 * 3600 + utc_delta.seconds
        seconds_to_wait = tries_renewal - utc_secs_now
        logger.warn("API Rate limit reached, seconds_till_renewal=%d", seconds_to_wait)
    logger.debug("Downloaded, tries_left=%d, tries_renewal=%d" % (tries_left, tries_renewal))
    return resp.read(), resp.info().getheader('Link'), seconds_to_wait


def parse_commit_links(content):
    jsondata = ujson.decode(content)

    res = []
    logger.debug("total_count=%s", str(jsondata["total_count"]))
    for item in jsondata["items"]:
        res.append(item["html_url"])
    logger.debug("found_commits=%d" % len(res))
    return res


def calculate_dates(in_date):
    now_minutes = datetime.datetime.strptime(in_date, '%Y%m%d%H%M')
    logger.info("datetime_minutes=%s" % now_minutes.isoformat())

    return (now_minutes - datetime.timedelta(minutes=1)).isoformat(), now_minutes.isoformat()


def main():
    if len(sys.argv) < 3:
        logger.error("Incorrect usage, needs:\n%s <Date in format YYYYMMDDHHmm> <output file>" % sys.argv[0])
        sys.exit(1)
    date_from, date_to = calculate_dates(sys.argv[1])
    filepath = sys.argv[2]

    template_url = \
        "https://api.github.com/search/commits?q=author-date:%s..%s%" \
        "%20is:public%%20merge:false&sort=author-date&order=desc&per_page=100"
    first_url = template_url % (date_from, date_to)
    partial_filepath = filepath + ".part"
    partial_file = open(partial_filepath, "w+")

    # First results page download
    written_urls_counter = 0
    content, links, time_to_wait = download_api_url(first_url)
    next_pages = get_next_pages(links)
    for commit_html_url in parse_commit_links(content):
        partial_file.write(commit_html_url)
        partial_file.write('\n')
        written_urls_counter += 1

    for page_url in next_pages:
        if time_to_wait > 0:
            # We have 10 requests per minute usually, let's sleep until a minute is past (add 1 second for safety)
            time_to_wait += 1
            logger.warn("Rate limit reached, sleeping for %d seconds..." % time_to_wait)
            time.sleep(time_to_wait)
            logger.warn("Continuing...")
        content, links, time_to_wait = download_api_url(page_url)
        for commit_html_url in parse_commit_links(content):
            partial_file.write(commit_html_url)
            partial_file.write('\n')
            written_urls_counter += 1

    partial_file.close()
    os.rename(partial_filepath, filepath)
    logger.info("Wrote commit_urls_count=%d to output_file=%s" % (written_urls_counter, filepath))


if __name__ == "__main__":
    main()
