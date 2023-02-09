"""
===================================
Tiered Harvest tests
===================================
"""
import logging
import os
import time
import csv
import codecs
import urllib.request
import urllib.parse
import urllib.error

import libx.filex
from harvesters.harvester_config import HarvesterAPWG
from lib.db.mdbthf import MongoWrapthfDB
from harvesters.harvester import Harvester
from harvesters.harvester import SandboxedHarvesterTest


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [str(cell, 'UTF-8') for cell in row]


import runtime

SUC_FILE_NAME = runtime.data_path + '/tsw/harvesters/thf/simple_url_canonicalizer.csv'
APWG_DATA_TMPL = '''"EBAY",2013-01-22 05:32:44,%(score)s,"%(url)s","%(nurl)s",URL'''


class SimpleUrlCanonicalizer(SandboxedHarvesterTest):
    default_har_config = HarvesterAPWG

    def __test_normalization_base(self, source_file, tcid):
        """ Run harvester for thf normalization tests"""
        logging.info("Starting Harvester for Testcase : " + tcid)
        hobj = Harvester(HarvesterAPWG())
        hobj.clean_working_dir()
        libx.filex.put_files_in_target(source_file,
                                       self.default_har_config.working_dir,
                                       create_target_path=True)
        if os.name != 'nt':
            if not hobj.run_harvester(None):
                logging.error('Harvester Execution: FAIL for test: %s' % tcid)
                raise AssertionError("Harvester Execution: FAIL")
        logging.info('Harvester Execution: ok for test: %s' % tcid)
        time.sleep(2)  # why sleep?

    def test_suc(self):
        """
        """
        # init vars
        hobj = Harvester(HarvesterAPWG())
        hobj.clean_working_dir()
        mongo_obj = MongoWrapthfDB("tieroneurl")
        apwg_data = []
        source_file = 'suc_test.xml'

        url_t = tuple(csv.reader(open(SUC_FILE_NAME)))
        # convert to APWG format
        for ourl, nurl in url_t:
            # delete data from mongodb for each of the URLs
            mongo_obj.thf_remove_normalized_url(nurl)
            doc = mongo_obj.thf_fetch_one_normalized_url(nurl)
            if doc:
                raise Exception('Unable to delete doc in mongodb for' \
                                + ' ourl:%s nurl: %s' % (ourl, nurl))
            logging.debug('Deleting:' + str(ourl, 'UTF-8'))
            line = str(APWG_DATA_TMPL % {'score': '10',
                                         'url': ourl,
                                         'nurl': urllib.parse.quote_plus(nurl).replace('/', '%2F'),
            }, 'UTF-8')
            apwg_data.append(line)

            # write apwg file in current dir
        logging.info('Creating file in current dir: %s' % source_file)
        with codecs.open(source_file, 'w+', encoding='utf-8') as fpw:
            for line in apwg_data:
                fpw.write(line)
                fpw.write(codecs.encode('\n', 'utf-8'))

                # run the harvester
        self.__test_normalization_base(source_file, 'suc_apwg')

        # mongo db checks
        errs = []
        oks = []
        mongo_obj = MongoWrapthfDB("tieroneurl")
        for ourl, nurl in url_t:
            doc = mongo_obj.thf_fetch_one_normalized_url(nurl)
            if not doc:
                errs.append('MongoDB: Doc not found for ourl: %s' % ourl \
                            + ' nurl: %s' % nurl)
                continue
            oks.append('Doc for ourl: %s was found ' % ourl \
                       + 'with nurl: %s' % nurl)

            if not ourl in doc["originalUrls"]:
                errs.append('MongoDB: nurl: %s ourl: ' % nurl \
                            + '%s not found in the set of original urls' % ourl)
                continue
            oks.append('Match: ourl and nurl match for ourl: %s' % ourl)
        logging.info('\n'.join(oks))
        logging.error('Mismatch count: %s' % len(errs))
        logging.error('\n'.join(errs))
