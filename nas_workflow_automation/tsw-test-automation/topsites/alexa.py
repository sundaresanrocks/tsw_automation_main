import os
import subprocess
import random
import string
from datetime import date

# Constants
URL_COUNT = 1000000
TLD_LIST = [".com", ".co.uk", ".edu", ".gov.uk", ".gov.ie"]
DIR_PREFIX = "/tmp/top-1m.csv"
LOADER_PATH = "/opt/sftools/bin/topsites_loader.sh"

CSV_FILE = "top-1m.csv"
SOURCE = "/tmp"
DEST = "/tmp"
ARCHIVEDIR = "/tmp/archive"
ARCHIVEFILE = "top-1m_"
CSV_EXT = ".csv"


# Run the loader with a valid input file, and confirm success.
def test_alexa_success():
    # Generate input files with random URLs
    make_rankings(URL_COUNT)

    # Run loader script
    cmd = LOADER_PATH + " file://" + SOURCE + " " + DEST + "/" + CSV_FILE
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

    # Check that loader script copied the CSV file to its destination
    assert os.path.exists(DEST + "/" + CSV_FILE)

    # Get the current timestamp
    present_date = date.today().strftime('%Y%m%d')

    # Check that a file is copied to the archive directory
    assert os.path.exists(ARCHIVEDIR + "/" + ARCHIVEFILE + present_date + CSV_EXT)

    # Clean up the archive file
    os.remove(ARCHIVEDIR + "/" + ARCHIVEFILE + present_date + CSV_EXT)

    # Clean up CSV file from destination dir
    os.remove(DEST + "/" + CSV_FILE)

    # Clean up Zip file from source dir
    os.remove(SOURCE + "/" + CSV_FILE + ".zip")

    assert proc.returncode == 0


def test_alexa_invalid_file_length_plus_1():
    load_bad_file(URL_COUNT + 1)


def test_alexa_invalid_file_length_minus_1():
    load_bad_file(URL_COUNT - 1)


def test_alexa_invalid_file_length_too_short():
    load_bad_file(URL_COUNT / 1000)


def test_alexa_invalid_file_length_zero():
    load_bad_file(0)


def test_alexa_inaccessible_archive():
    load_bad_file(URL_COUNT, "/usr")


def test_alexa_incorrect_filename():
    load_bad_file(URL_COUNT, prefix="new-")


# Run the loader with an invalid input file, and confirm failure.
def load_bad_file(entry_count, source_dir=SOURCE, prefix=""):
    # Generate input files with random URLs
    make_rankings(entry_count, prefix)

    # Run loader script
    cmd = LOADER_PATH + " " + "file://" + source_dir + " " + DEST + "/" + prefix + CSV_FILE
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

    # Clean up CSV file from working dir if still present
    if os.path.exists(prefix + CSV_FILE):
        os.remove(prefix + CSV_FILE)

    # Clean up Zip file from source dir
    os.remove(SOURCE + "/" + CSV_FILE + ".zip")

    # Check that loader script didn't copy the CSV file to its destination
    assert not os.path.exists(DEST + "/" + prefix + CSV_FILE)

    # Get the current timestamp
    present_date = date.today().strftime('%Y%m%d')

    # Check that a file is NOT copied to the archive directory
    assert not os.path.exists(ARCHIVEDIR + "/" + ARCHIVEFILE + present_date + CSV_EXT)

    assert proc.returncode != 0


# Create an artificial rankings text file with the specified number of entries, and place it within a Zip archive.
# An optional prefix for the text file can be specified for the purpose of creating an unexpected file name.
def make_rankings(entry_count, prefix=""):
    file = open(SOURCE + "/" + prefix + CSV_FILE, "w")
    for x in range(1, entry_count + 1):
        domain_len = random.randint(13, 37)
        domain = ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(domain_len))
        end = random.choice(TLD_LIST)
        url = domain + end
        file.write(str(x) + "," + url + "\n")
    file.close()

    # Add rankings list to a Zip archive
    cmd = "zip -j " + SOURCE + "/" + CSV_FILE + ".zip " + SOURCE + "/" + prefix + CSV_FILE
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    assert proc.returncode == 0
    os.remove(SOURCE + "/" + prefix + CSV_FILE)
