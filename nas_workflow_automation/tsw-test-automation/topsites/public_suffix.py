# -*- coding: utf-8 -*-

import os
import subprocess
import random
import string


# Constants
LINE_COUNT = 100
SUFFIX_LIST = ["ballooning.aero", "1.bg", "*.ck", "!www.ck", "*.er", "*.kawasaki.jp", "!city.kawasaki.jp",
    "steam.museum", "ålgård.no", "cc.mn.us", "yachts", "youtube", "//"]
DIR_PREFIX = "/tmp/top-1m.csv"
LOADER_PATH = "/opt/sftools/bin/public_suffix_loader.sh"
SUFFIX_FILE = "test.dat"
SOURCE = "/tmp"
DEST = "/tmp/psl/"
ICANN_BEGIN = "// ===BEGIN ICANN DOMAINS==="
ICANN_END = "// ===END ICANN DOMAINS==="


# Run the loader with a valid input file, and confirm success.
def test_success():
    # Generate input files with random URLs
    make_suffix_file(LINE_COUNT)

    # Run loader script
    cmd = LOADER_PATH + " file://" + SOURCE  + "/" + SUFFIX_FILE + " " + DEST
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

    # Check that loader script copied the suffix file to its destination
    assert os.path.exists(DEST + "/" + SUFFIX_FILE)

    # Check that the correct entries and characters have been excluded/preserved
    file = open(DEST + "/" + SUFFIX_FILE, "r")
    new_contents = file.read()
    assert new_contents.count("//") == 0
    assert new_contents.count(" ") == 0
    assert new_contents.count("\t") == 0
    assert new_contents.count("*") == 0
    assert new_contents.count("!") == 0
    assert new_contents.count("å") > 0
    assert new_contents.count("youtube") == 0

    # Clean up suffix file from destination dir
    os.remove(DEST + "/" + SUFFIX_FILE)

    # Clean up suffix file from source dir
    os.remove(SOURCE + "/" + SUFFIX_FILE)

    assert proc.returncode == 0


# Check that the script fails gracefully when an empty file is input
def test_empty():
    expect_fail(0, False, False)


# Check that the script fails gracefully when beginning marker is missing
def test_missing_begin_marker():
    expect_fail(LINE_COUNT, False, True)


# Check that the script fails gracefully when end marker is missing
def test_missing_end_marker():
    expect_fail(LINE_COUNT, True, False)


# Check that the script fails gracefully when both beginning and end markers are missing
def test_missing_markers():
    expect_fail(LINE_COUNT, False, False)


# Check that the script fails gracefully when the source file is inaccessible or doesn't exist
def test_no_file():
    expect_fail(-1)


# Check that an empty file is produced when all non-comment lines begin with whitespace
def test_leading_whitespace():
    # Generate input files with random URLs
    make_suffix_file(LINE_COUNT, True, True, True)

    # Run loader script
    cmd = LOADER_PATH + " file://" + SOURCE  + "/" + SUFFIX_FILE + " " + DEST
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

    # Check that loader script copied the suffix file to its destination
    assert os.path.exists(DEST + "/" + SUFFIX_FILE)

    file = open(DEST + "/" + SUFFIX_FILE, "r")
    new_contents = file.read()
    assert len(new_contents) == 0

    # Clean up suffix file from destination dir
    os.remove(DEST + "/" + SUFFIX_FILE)

    # Clean up suffix file from source dir
    os.remove(SOURCE + "/" + SUFFIX_FILE)

    assert proc.returncode == 0


# Run the script and check that it fails.
# entry_count - number of suffix entries/comments to create in the test input file, or -1 to not create an input file.
# insert_begin_marker - True if the ICANN Domains section beginning marker should be added to the file.
# insert_begin_marker - True if the ICANN Domains section end marker should be added to the file.
def expect_fail(entry_count, insert_begin_marker=True, insert_end_marker=True):
    # Generate input files with random URLs
    if entry_count >= 0:
        make_suffix_file(entry_count, insert_begin_marker, insert_end_marker)

    # Run loader script
    cmd = LOADER_PATH + " file://" + SOURCE  + "/" + SUFFIX_FILE + " " + DEST
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    assert proc.returncode != 0

    # Check that loader script didn't copy the suffix file to its destination
    assert not os.path.exists(DEST + "/" + SUFFIX_FILE)

    # Clean up suffix file from source dir
    if entry_count >= 0:
        os.remove(SOURCE + "/" + SUFFIX_FILE)


# Create an artificial suffix list text file with the specified number of entries.
# An optional prefix for the text file can be specified for the purpose of creating an unexpected file name.
def make_suffix_file(entry_count, insert_begin_marker=True, insert_end_marker=True, start_with_whitespace=False):
    file = open(SOURCE + "/" + SUFFIX_FILE, "w")
    if insert_begin_marker:
        file.write(ICANN_BEGIN + "\n")

    for x in range(entry_count):
        domain_len = random.randint(1, 40)
        whitespace = random.choice(" \t")

        # Select one of the sample suffixes at random
        comment = "".join(
            random.choice(string.ascii_lowercase + " \t")
            for _ in range(domain_len))
        suffix = random.choice(SUFFIX_LIST)

        # If requested, start every entry line with a space or tab
        if start_with_whitespace and suffix != "//":
            start_whitespace = random.choice(" \t")
        else:
            start_whitespace = ""

        # Write approximately half of the entries with a trailing comment, and the rest without
        if random.choice([True, False]):
            file.write(start_whitespace + suffix + whitespace + comment + "\n")
        else:
            file.write(start_whitespace + suffix + "\n")

    if insert_end_marker:
        file.write(ICANN_END + "\n")
    file.close()

