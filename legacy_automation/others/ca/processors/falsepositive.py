# ================================================
#    FALSE POSITIVE REPORTING : WEB-QA
# ================================================

__author__ = 'avimehenwal'

import os
import pdb
import json
import pprint
import datetime
import logging
import xlsxwriter
from operator import itemgetter
from collections import OrderedDict
from bson.objectid import ObjectId

from clients import SUPPORTED_CLIENTS
import processors.canonicalizer as canon

try:
    import pymongo
except:
    logging.error('Import ERROR : pymongo module')

FORMAT = '%(asctime)-15s %(message)s'
# logging.basicConfig(filename='myapp.log', level=logging.INFO, format=FORMAT)
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

class URLCloudLooker:

    def __init__(self, threads, test_type, client='sdkclient'):
        if client not in SUPPORTED_CLIENTS:
            _err_msg = "client %s is does not exist." % client
            logging.error(_err_msg)
            raise NotImplementedError(_err_msg)
        if test_type not in ['fp', 'fn']:
            raise ValueError('test_type must be either fp or fn')
        if test_type == 'fp':
            self.title = 'False Positive tests'
        if test_type == 'fn':
            self.title = 'False Negative tests'
        self.subject = ''
        self.test_type = test_type
        self.report = []
        self.summary = []
        try:
            self.client = pymongo.MongoClient('172.19.216.125', 27017)
            print('Mongodb Connection Successful ',self.client)
        except:
            logging.error('Cannot connect to mongodb : Please check if server is running')
        # self.db = self.client.avi_1                # for testing
        self.db = self.client.falsepositive         # for production
        self._looker = SUPPORTED_CLIENTS[client]['class'](config=SUPPORTED_CLIENTS[client],
                                                          threads=threads)

    @staticmethod
    def _load_urls_from_file(input_file):
        """
        Loads the list of urls from file. This method trims blank spaces and ignores lines starting with #
        :param input_file: valid text file
        :return: list of urls [avi]: return url with index in file (Alexa Rank)
        """
        if not os.path.isfile(input_file):
            logging.error('File not found: %s' % input_file)
            raise FileNotFoundError(input_file)
        fp = open(input_file)
        rank_url = []
        for k, v in enumerate(fp, start=1):
            v = v.strip()
            if not v.startswith('#'):
                rank_url.append((k, v))
            else:
                logging.info("Ignored url : %s" % v)
        return rank_url

    def _classify_urls(self, urls, url_results, write_to_xlsx='result.xlsx'):
        """ Add url colour based on category to url_results """
        ret_value = OrderedDict({'error': [],
                                 'green': [],
                                 'yellow': [],
                                 'gray': [],
                                 'red': [],
                                 'last_checked_date': datetime.datetime.utcnow()})

        def write_line(work_sheet, url_row, url_inner, data):
            work_sheet.write_row(url_row, 0, (url_inner, data['alexa_rank'], data['rep'], data['cats'], data['attr_flags'], data['ms'], data['geo'], data['reviewed']))

        def check_reviewed_state(url_result):
            ''' Get verified status from mongoDB and add them in list.
            :param: url
            :return: Boolean
            '''
            # url_meta = self.canonicalize_url(url)
            print(url_result)
            try:
                return self.db.url.find_one({"cl_hash" : url_result['canon']['cl-hash']})['reviewed']
                # return True
            except Exception as e:
                print("Exception Occoured for url [%s] : %s"%(url, e))
                return False

        # Added new column 'Reviewed' in worksheets
        header = 'URL,Alexa Rank,Reputation,Cat Codes,Attributes,Mcafee Secure,Geo,Reviewed'.split(',')
        work_book = xlsxwriter.Workbook(write_to_xlsx)
        s_work_sheet = work_book.add_worksheet('Summary')
        red_work_sheet = work_book.add_worksheet('Red')
        green_work_sheet = work_book.add_worksheet('Green')
        yellow_work_sheet = work_book.add_worksheet('Yellow')
        gray_work_sheet = work_book.add_worksheet('Gray')
        error_work_sheet = work_book.add_worksheet('Error')
        sheets_url = (red_work_sheet, green_work_sheet, gray_work_sheet, yellow_work_sheet)

        #### Write headers for URL sheets
        format_header = work_book.add_format({'bold': 1})
        for sheet in sheets_url:
            sheet.write_row(0, 0, header)
            sheet.set_row(0, 20, format_header)
            sheet.set_column('A:A', 50)

        gn_row = r_row = y_row = gy_row = e_row = 1
        for url in urls:
            ## logging.warning(url_results[url])
            try :
                if not url_results[url[1]]:
                    ret_value['error'].append(url[1])
                    # url_results[url]['color'] = 'error'
                    error_work_sheet.write_row(e_row, 0, (url[1]))
                    e_row += 1
                elif 'rep' not in url_results[url[1]]:
                    ret_value['error'].append(url[1])
                    url_results[url[1]]['color'] = 'error'
                    error_work_sheet.write_row(e_row, 0, (url_results[url[1]]))
                    e_row += 1
                elif url_results[url[1]]['rep'] <= 14:
                    ret_value['green'].append(url[1])
                    url_results[url[1]]['color'] = 'green'
                    url_results[url[1]]['reviewed'] = check_reviewed_state(url_results[url[1]])
                    write_line(green_work_sheet, gn_row, url[1], url_results[url[1]])
                    gn_row += 1
                elif url_results[url[1]]['rep'] <= 29:
                    ret_value['gray'].append(url[1])
                    url_results[url[1]]['color'] = 'gray'
                    url_results[url[1]]['reviewed'] = check_reviewed_state(url_results[url[1]])
                    write_line(gray_work_sheet, gy_row, url[1], url_results[url[1]])
                    gy_row += 1
                elif url_results[url[1]]['rep'] <= 49:
                    ret_value['yellow'].append(url[1])
                    url_results[url[1]]['color'] = 'yellow'
                    url_results[url[1]]['reviewed'] = check_reviewed_state(url_results[url[1]])
                    write_line(yellow_work_sheet, y_row, url[1], url_results[url[1]])
                    y_row += 1
                else:
                    ret_value['red'].append(url[1])
                    url_results[url[1]]['color'] = 'red'
                    url_results[url[1]]['reviewed'] = check_reviewed_state(url_results[url[1]])
                    write_line(red_work_sheet, r_row, url[1], url_results[url[1]])
                    r_row += 1
            except:
                print("Error with URL : ", url[1])
                error_work_sheet.write_row(e_row, 0, (url[1]))
                e_row += 1

        #### Create filter
            red_work_sheet.autofilter(0, 0, len(ret_value['red']), 5)
            green_work_sheet.autofilter(0, 0, len(ret_value['green']), 5)
            yellow_work_sheet.autofilter(0, 0, len(ret_value['yellow']), 5)
            gray_work_sheet.autofilter(0, 0, len(ret_value['gray']), 5)

        #### Write summary
        s_work_sheet.write_row(0, 0, ('Summary',), format_header)
        s_work_sheet.write_row(1, 0, ('Type', 'Count'), format_header)
        s_work_sheet.set_row(7, 20, format_header)
        # print(self._get_summary_tuples(ret_value))
        for row, value in enumerate(self._get_summary_tuples(ret_value)):
            # print (value)
            s_work_sheet.write_row(row+2, 0, value)

        #### Create chart
        pie_chart = work_book.add_chart({'type': 'pie'})
        pie_chart.set_title({'name': self.title})
        pie_chart.add_series(dict(name=self.title, categories='=Summary!A3:A7', values='=Summary!B3:B7', points=[
            {'fill': {'color': '#C0514E'}},
            {'fill': {'color': '#9CBB5A'}},
            {'fill': {'color': '#FFC004'}},
            {'fill': {'color': '#7D7D7D'}},
            {'fill': {'color': '#5C377D'}},
        ]))
        s_work_sheet.insert_chart('A10', pie_chart)

        work_book.close()

        return ret_value

    # def load_and_classify_urls_from_file(self, input_file):
    #     urls = self._load_urls_from_file(input_file)
    #     url_results = self._looker.process_urls(urls)
    #     return {'classify_urls' : self._classify_urls(urls, url_results),
    #             'urls' : urls,
    #             'url_results' : url_results
    #             }

    def _get_summary(self, urls_d):
        return 'Summary - %s:' % self.title + '\n-----------' + '-' * len(self.title) + \
               '\n'.join(['%s: %s' % (key[0], key[1]) for key in self._get_summary_tuples(urls_d)]) +\
               '\n-------------------------------------------\n'

    def _get_summary_tuples(self, urls_d):
        total = len(urls_d['red']) + len(urls_d['green']) + len(urls_d['yellow']) + len(urls_d['gray']) + len(
            urls_d['error'])
        return (('Red', len(urls_d['red'])),
                ('Green', len(urls_d['green'])),
                ('Yellow', len(urls_d['yellow'])),
                ('Gray', len(urls_d['gray'])),
                ('Errors', len(urls_d['error'])),
                ('Total', total))

    def get_colour(self, color):
        if color == 'red':
            colour_code = "#FF0000"
        elif color == 'green':
            colour_code = "#00FF00"
        elif color == 'yellow':
            colour_code = "#FFC004"
        elif color == 'gray':
            colour_code = "#7D7D7D"
        elif color == 'New':
            colour_code = "#00FFFF"
        else:
            colour_code = "#FFFFFF"
        result = """bgcolor="%s" """ % colour_code
        print(result)
        return result

    def table_block(self, alexa_rank=None, URL=None, Old_value=None, New_value=None):
        ''' Returns HTML table records in blocks '''
        code_new = self.get_colour(New_value)
        code_old = self.get_colour(Old_value)
        block = "<tr>" \
                    "<td>%(alexa)s</td>" \
                    "<td>%(url)s</td>" \
                    "<td %(code_old)s>%(old)s</td>" \
                    "<td %(code_new)s>%(new)s</td>" \
                "</tr>" % {'alexa' : alexa_rank,
                           'url'    : URL,
                           'code_old' : code_old,
                           'old'    : Old_value,
                           'code_new': code_new,
                           'new'    : New_value }
        print(block)
        return block

    def _get_html_summary(self, urls_d, updated=None, new_addition=None):
        """
        :param urls_d: List of dictionaries with category as the keys
        :return: Returns HTML summary table for mail
        """
        summary2 = summary3 = summary4 = ''
        if updated or new_addition:
            print('*'*100)
            a = '</br>'
            b = '<h3> Classification changes from New, Green, Grey, or Yellow to <font color=#C0514E>RED</font>  </h3>'
            f = '<h3> Classification changes from New, Green, Grey, to <font color=#FFC004>YELLOW</font>  </h3>'
            # g = '<h3> Classification changes to <font color=#7D7D7D>OTHERS</font>  </h3>'
            c = '''<table border=1>
                  <tr>
                    <th>Alexa Rank</th>
                    <th>URL</th>
                    <th>Old Classification</th>
                    <th>New Classification</th>
                  </tr>
            '''
            red_table = c
            yellow_table = c
            # others_table = c

            if updated:
                print('No of urls seen with updated classification : ', len(updated))
                for item in updated:
                    url = item['new_values']['canon']['original-url']
                    alexa_rank = item['new_values']['alexa_rank']
                    for cat in item['changes']:
                        if list(cat.keys())[0] == 'color':
                            old = cat[list(cat.keys())[0]]['old_val']
                            new = cat[list(cat.keys())[0]]['new_val']
                            print('AlexaRank = ', alexa_rank )
                            print('URL=', url)
                            print('Old_value=', old)
                            print('New_value=', new)
                            element = self.table_block(alexa_rank=alexa_rank, URL=url, Old_value=old, New_value=new)
                            if new == 'red':
                                red_table = red_table + element
                            elif new == 'yellow':
                                if old != 'red':
                                    yellow_table = yellow_table + element
                            # else:
                            #     others_table = others_table + element
            if new_addition:
                print('No of new urls seen : ', len(new_addition))
                for doc in new_addition:
                    url = doc['original_url']
                    alexa_rank = doc['historic_data'][0]['alexa_rank']
                    old = 'New'
                    new = doc['current_color']
                    element = self.table_block(alexa_rank=alexa_rank, URL=url, Old_value=old, New_value=new)

                    if new == 'red':
                        red_table = red_table + element
                    elif new == 'yellow':
                        if old != 'red':
                            yellow_table = yellow_table + element
                    # else:
                    #     others_table = others_table + element

            e = ''' </table>'''
            if red_table != c:
                summary2 = a + b + red_table + e
            if yellow_table != c:
                summary3 = a + f + yellow_table + e
            # if others_table != c:
            #     summary4 = a + g + others_table + e
            print(summary2)
            print(summary3)
            # pdb.set_trace()
            # print(type(summary2))
        else:
            logging.info('No updates data to be added in Email Report')
            summary2 = '</br><h3> No changes recorded this run </h3>'

# [avi] : No new urls added info required in Email
        # if new_urls_added:
        #     print('*'*100)
        #     a = "</br><h3>New Urls Added this run </h3>"
        #     b = '''<table border=1>
        #           <tr>
        #             <th>URL</th>
        #           </tr>
        #     '''
        #     e = ''' </table>'''
        #     if isinstance(new_urls_added, list):
        #         for url in new_urls_added:
        #             c = "<tr> <td>%s</td> </tr>" %(url)
        #             b = b + c
        #     summary3 = a + b + e
        # else:
        #     logging.info('No new urls added sent to Email Report')
        #     summary3 = '</br><h3> No new urls added this run </h3>'

        return '<h3>Summary - %s</h3>' % self.title + \
               '\n<table border=1>' + \
               '\n<tr><th width=125>Classification Type</th><th width=50>Count</th></tr>' + \
               '\n<tr><font color=#C0514E><td>Red</td><td align=right>%s</font></td></tr>' % len(urls_d['red']) + \
               '\n<tr><font color=#9CBB5A><td>Green</td><td align=right>%s</font></td></tr>' % len(urls_d['green']) + \
               '\n<tr><font color=#FFC004><td>Yellow</td><td align=right>%s</font></td></tr>' % len(urls_d['yellow']) +\
               '\n<tr><font color=#7D7D7D><td>Gray</td><td align=right>%s</font></td></tr>' % len(urls_d['gray']) + \
               '\n<tr><font color=#5C377D><td>Errors</td><td align=right>%s</font></td></tr>' % len(urls_d['error']) + \
               '\n<tr><td><b>Total</td><td align=right>%s</b></td></tr>' % (len(urls_d['error']) +
                                                                            len(urls_d['green']) +
                                                                            len(urls_d['yellow']) +
                                                                            len(urls_d['gray']) +
                                                                            len(urls_d['red'])) + \
               '\n</table>'+summary2+summary3+'</br>'

    def get_reputation_color(self, cl_hash):
        ''' OBSELETE
        :param cl_hash:
        :return: colour for the cl_hash
        '''
        return self.db.url.find_one({"cl_hash" : cl_hash},{"reputation_color" :1, "_id":0})['reputation_color']

    def compare_and_update(self, baseDoc, newValue):
        ''' Compares current changes with previous once and updates in db
        :param baseDoc: Mongo document in dict format
        :param newValue: url score and category from client in dict
        :return: (baseDoc, newValue, whatChanged) and  if changes are found else False
        '''
        try:        # Removing ObjectId from dict as its binary formatted and print gives AttribbuteError
            del baseDoc['_id']
        except KeyError:
            print('ERROR')
            pass
        self.db.url.update({"cl_hash" : baseDoc['cl_hash']},{"$set": {"last_seen":newValue['date'] }})
        add_subdocument = False
        changed = []
        if baseDoc['current_color'] != newValue['color']:
            print('Change in color detected ! previous %s new %s'%(baseDoc['current_color'], newValue['color'] ))
            change = {'color' : {  'old_val' : baseDoc['current_color'],
                                    'new_val' : newValue['color']
            }}
            changed.append(change)
            self.db.url.update({"cl_hash" : baseDoc['cl_hash']}, {"$set" : {
                "previous_color" : baseDoc['current_color'] ,
                "current_color"  : newValue['color']           }})

            add_subdocument = True

        if baseDoc['current_score'] != newValue['rep']:
            # try:
            print('Change in score detected ! previous %s new %s'%(baseDoc['current_score'], newValue['rep'] ))
            change = {'rep' : {  'old_val' : baseDoc['current_score'],
                                 'new_val' : newValue['rep']
            }}
            changed.append(change)
            self.db.url.update({"cl_hash" : baseDoc['cl_hash']}, {"$set" : {
                "previous_score" : baseDoc['current_score'] ,
                "current_score"  : newValue['rep']           }})
            add_subdocument = True
            # except Exception as e:
            #     print("Exception occoured : ",e)
            #     pdb.set_trace()
                # return False


        if baseDoc['current_cat'] != newValue['cats']:
            print('Change in cat detected ! previous %s new %s'%(baseDoc['current_cat'], newValue['cats'] ))
            change = {'cats' : {  'old_val' : baseDoc['current_cat'],
                                 'new_val' : newValue['cats']
            }}
            changed.append(change)
            self.db.url.update({"cl_hash" : baseDoc['cl_hash']}, {"$set" : {
                "previous_cat" : baseDoc['current_cat'] ,
                "current_cat"  : newValue['cats']           }})
            add_subdocument = True

        if baseDoc['current_ms'] != newValue['ms']:
            print('Change in ms detected ! previous %s new %s'%(baseDoc['current_ms'], newValue['ms'] ))
            change = {'ms' : {  'old_val' : baseDoc['current_ms'],
                                 'new_val' : newValue['ms']
            }}
            changed.append(change)
            self.db.url.update({"cl_hash" : baseDoc['cl_hash']}, {"$set" : {
                "previous_ms" : baseDoc['current_ms'] ,
                "current_ms"  : newValue['ms']           }})
            add_subdocument = True

        if add_subdocument:
            print("Adding Subdocument to base document")
            print(newValue)
            print(type(newValue))
            self.db.url.update({"cl_hash" : baseDoc['cl_hash']},
                               { "$push" : { "historic_data" : newValue }})
            return {
                'old_doc'    : baseDoc,
                'new_values' : newValue,
                'changes'    : changed
            }
        else:
            print('Nothing to update for url : ', baseDoc['canon_url'])
        return False


    def canonicalize_url(self, url):
        if canon.get_canon_url(url) is False:
            msg = url + '\t cannnot be canonicalised by canonicalizer !!! Skipped'
            print(msg)
            with open('canon_error.log', 'a+') as fpw:
                print(fpw)
                print(fpw.write(str(msg+"\n")))
            return False
        else:
            return canon.get_canon_url(url)


    def data_in_mongo_format(self, data=None):
        '''
        :param data: json returned from  load_and_classify_urls_from_file() method
        :return: list of dictionaries for readily pushing values in mongo
        NOTE : assumes all urls are new. Need to add logic to check if already saved url in encountered
        Seperate update query for that.
        '''
        if isinstance(data, dict):
            docs_newly_added = []
            docs_found_updated = [] # list of dictionaries
            for url in data.keys():
                client_results = data[url]
                # print('processing URL : ', client_results)
                client_results['date'] = datetime.datetime.utcnow()
                if client_results['canon']:
                    record = self.db.url.find_one({"cl_hash" : client_results['canon']['cl-hash'] })
                    if record:
                        logging.info("URL %s already in database"%(client_results['canon']['canon-url']))
                        updated_record = self.compare_and_update(record, client_results)
                        # logging.info(pprint.pformat(updated_record))
                        if isinstance(updated_record, dict):
                            docs_found_updated.append(updated_record)
                        # print('%s updated with %s'%(url_meta['canon-url'], client_results))
                    else:
                        result = { "original_url" :  client_results['canon']['original-url'],
                                   "canon_url" : client_results['canon']['canon-url'],
                                   "cl_hash" : client_results['canon']['cl-hash'],
                                   "first_seen" : client_results['date'],
                                   "last_seen" : client_results['date'],
                                   "previous_color" : client_results['color'],
                                   "current_color" : client_results['color'],
                                   "previous_score" : client_results['rep'],
                                   "current_score" : client_results['rep'],
                                   "previous_cat" : client_results['cats'],
                                   "current_cat" : client_results['cats'],
                                   "previous_ms" : client_results['ms'],
                                   "current_ms" : client_results['ms'],
                                   "historic_data" : [client_results],
                                 }
                        docs_newly_added.append(result)
                        print("URL %s NOT in database ... Added !"%(client_results['canon']['canon-url']))
            logging.info(docs_found_updated)
            return {
                'add'     : docs_newly_added,
                'updated' : docs_found_updated
            }
        else:
            print('Please provide a Python Dict object in argument')
            return False

    def fn_fp_tests(self, input_file, add_detailed_report=True):
        subject_suffix = ''
        logging.info('Executing - %s' % self.title)
        new_urls_added = None
        rank_url = self._load_urls_from_file(input_file)
        # print('rank_url\n', rank_url)
        url_results = self._looker.process_urls(rank_url)
        # print(url_results)
        urls_d = self._classify_urls(rank_url, url_results)
        print(urls_d)
        data_dict = self.data_in_mongo_format(data=url_results)
        # pprint.pformat(data_dict, indent=15)

        logging.info("SUMMARY:")
        if len(data_dict['add']) > 0 :
            new_urls_added = []
            for doc in data_dict['add']:
                logging.debug(doc)
                self.db.url.save(doc)
                new_urls_added.append(doc['original_url'])
            logging.info("NEW URLs added this run : %s", len(new_urls_added))
        else:
            logging.info('No new URLs added in this run')

        classification_changed_docs = None
        new_addition = None
        # sorted_updates = sorted(data_dict['updated'], key=itemgetter('name'))
        if len(data_dict['updated']) > 0 or len(data_dict['add']) > 0:
            logging.info('No of URL Updates Found this run : %s', len(data_dict['updated']))
            updated = data_dict['updated']
            new_addition = data_dict['add']
            # pdb.set_trace()
            classification_changed_docs = self.get_classification_updates(updated)

            # print(data_dict['updated'])
            # print(type(data_dict['updated']))
            # for doc in data_dict['updated']:
                # print(doc)
                # logging.debug('%s', doc) # Logging Error : msg = msg % self.args
        else:
            logging.info('No Updates Found in URLs')


        summary = self._get_html_summary(urls_d, classification_changed_docs, new_addition)
        self.summary.extend(summary)
        # logging.info(summary)

        # ### detailed reports
        detail_report = ['\nDetailed report- %s\n' % self.title + '------------------%s' % ('-' * len(self.title))]
        if len(urls_d['error']) > 0:
            detail_report.append('\nerror urls:\n-----------\n' + '\n'.join(urls_d['error']))
        # skip green urls for false negative tests
        # skip green urls for false positive tests
        if self.test_type == 'fp':
            subject_suffix = '(%s red, ' % len(urls_d['red'])
            if len(urls_d['red']) > 0:
                detail_report.append('\nred urls:\n---------\n' + '\n'.join(urls_d['red']))

        if self.test_type == 'fn':
            subject_suffix = '(%s green, ' % len(urls_d['green'])
            if len(urls_d['green']) > 0:
                detail_report.append('\ngreen urls:\n-----------\n' + '\n'.join(urls_d['green']))

        subject_suffix += '%s yellow, ' % len(urls_d['yellow'])
        subject_suffix += '%s gray)' % len(urls_d['gray'])
        if len(urls_d['gray']) > 0:
            detail_report.append('\ngray urls:\n----------\n' + '\n'.join(urls_d['gray']))
        if len(urls_d['yellow']) > 0:
            detail_report.append('\nyellow urls:\n------------\n' + '\n'.join(urls_d['yellow']))

        if add_detailed_report:
            self.report.extend(detail_report)

        # writing logs
        with open('error.log', 'w') as fpw:
            fpw.write('\n'.join(urls_d['error']))
        with open('green.log', 'w') as fpw:
            fpw.write('\n'.join(urls_d['green']))
        with open('gray.log', 'w') as fpw:
            fpw.write('\n'.join(urls_d['gray']))
        with open('yellow.log', 'w') as fpw:
            fpw.write('\n'.join(urls_d['yellow']))
        with open('red.log', 'w') as fpw:
            fpw.write('\n'.join(urls_d['red']))

        return subject_suffix, summary, detail_report

    def mcafee_secure_tests(self, input_file, add_to_report=True):
        logging.info('Executing McAfee secure tests')
        logging.critical('Not yet implemented!')
        logging.warning('{} {}' .format(input_file, add_to_report))

    def set_reviewed(self, input_file):
        d = datetime.datetime.now()
        fail_count = 0
        with open(input_file, 'r+') as fpw:
            for line in fpw :
                can_url = self.canonicalize_url(line)
                if can_url:
                    logger.info('Updating for : %s'%(can_url['canon-url']))
                    upd = self.db.url.update({"cl_hash" : can_url['cl-hash']}, {"$set" : {
                                                    "reviewed" : True ,
                                                    "reviewed_date"  : d   }})
                    logger.info("Update Status : %s"%(upd))
                    if not upd['updatedExisting']:
                        fail_count += 1
                        logger.critical("No record update by query : Saving url")
                        with open("reviewFailedURLs.txt", "w") as file:
                            file.write(line)
                            logger.info('url written : %s'%(line))
                else:
                    print('Cannot review URL : ', line)
            logger.info("finished reading file")
        logger.info("URLs not found and updated as reviewed in db saved in reviewFailedURLs.txt file COUNT = %d"%(fail_count))
        return True


    def get_classification_updates(self, updated):
        """ Checks and considers only the reputation updates from input data """
        if isinstance(updated, list):
            classification_changed_andnew = []
            for item in updated:
                consider_doc = False
                for sub in item['changes']:
                    if 'color' in sub.keys():
                        consider_doc = True
                if consider_doc:
                    classification_changed_andnew.append(item)
            logging.debug(classification_changed_andnew)
            # pdb.set_trace()
            if classification_changed_andnew:
                return classification_changed_andnew
            else:
                return None


## Test
# if __name__ == '__main__':
#     url = URLCloudLooker()
#     print(url.set_reviewed())
#     print('success')



