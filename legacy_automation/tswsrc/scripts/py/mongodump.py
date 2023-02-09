"""
======================
Mongodb dump creator
======================

This utility helps create mongodb dumps for selective collections in a particular database. Host, port and user creds are taken from environment variables.
"""
import sys

from lib.db.mongowrap import get_qa_mongo_wrap


def dumper(db, collection, filename):
    """
    create dump to the given file
    """
    mobj = get_qa_mongo_wrap(collection, db)
    mobj.dump_collection_to_file(filename)

if __name__ == '__main__':

    if len(sys.argv) == 4:
        mdb = str(sys.argv[1])
        _collection = str(sys.argv[2])
        _filename = str(sys.argv[3])
        dumper(mdb, _collection, _filename)
    else:
        print('Usage: python mongodump.py databasename collectionname filename.dump')