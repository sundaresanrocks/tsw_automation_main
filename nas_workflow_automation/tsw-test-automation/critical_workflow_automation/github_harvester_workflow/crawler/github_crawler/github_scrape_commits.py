from bs4 import BeautifulSoup
import urllib2
import re
import wsr_logger
import multiprocessing
import sys

logger = wsr_logger.get_logger("python.github_commit_scraper")


def to_usercontent_url(in_url, filepath):
    res = re.sub(r"/commit/[0-9a-f]{40}", "/master", in_url, 1)
    res = res.replace("https://github.com/", "https://raw.githubusercontent.com/", 1)
    return (res + "/" + filepath).replace(" ", "%20")


def find_exes(in_url):
    logger.debug("Downloading commit_url=%s" % in_url)
    content = urllib2.urlopen(in_url).read()
    if content.lower().find(".exe") < 0:
        # No need to parse if there is no .exe to be found
        return []
    soup = BeautifulSoup(content, 'html.parser')

    res = []
    for item in soup.find_all('a'):
        try:
            filepath = item.get("title")
            if filepath is None or len(filepath) < 1:
                continue
            if filepath.lower().endswith(".exe"):
                exe_url = to_usercontent_url(in_url, filepath)
                logger.info("Found exe in url=%s" % exe_url)
                res.append(exe_url)
        except:
            logger.exception("Error reading item='%s'" % item)
    return res


def worker(line):
    exe_urls = []
    commit_url = line.strip()
    if len(commit_url) > 0:
        try:
            exe_urls += find_exes(commit_url)
        except:
            logger.exception("Error downloading from url='%s" % commit_url)
    return exe_urls


def main():
    input_file = open(sys.argv[1])
    lines = input_file.readlines()
    input_file.close()
    # Dinamically adjust number of workers:
    #   we want to complete N downloads that take up to 3 seconds in under 1 minute
    # minimum workers = 5, maximum workers = 100
    n_workers = max(5, min(len(lines) * 3 / 60, 100))
    logger.info("Scraping using n_workers=%d" % n_workers)
    pool = multiprocessing.Pool(n_workers)
    res = reduce(lambda a, b: a + b, pool.map(worker, lines))

    # remove duplicates
    res = set(res)
    logger.info("Found exe_count=%d exes" % len(res))

    if len(res) > 0:
        output_file = open(sys.argv[2], "w+")
        output_file.write(u"\n".join(res).encode('utf-8'))
        output_file.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("argv=%s", str(sys.argv))
        logger.error("Incorrect usage, needs:\n%s <input file> <output file>" % sys.argv[0])
        sys.exit(1)
    main()
