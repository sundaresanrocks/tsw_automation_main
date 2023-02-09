"""

crontab
*******
20 0 * * * cd /home/toolguy/src; source /home/toolguy/tswenv/bin/activate; export PYTHONPATH=/home/toolguy/src; rm -f top-1m.csv; rm -f top-1m.csv.zip; wget http://s3.amazonaws.com/alexa-static/top-1m.csv.zip; unzip top-1m.csv.zip; head -5000 top-1m.csv | awk -F ',' '{print $2};' > alexa-5k.txt;python ca/false_positive_script.py alexa-5k.txt -fp -t 100 -e m &>>fp.log
"""
__author__ = 'manoj'

import os
import sys
import argparse
import logging
import datetime
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart, MIMEBase
from email import encoders
# from ca.clients import SUPPORTED_CLIENTS
# print(sys.path)
from ca.processors.falsepositive import URLCloudLooker


FROM_EMAIL = 'Srinivasan_GN@McAfee.com'
SMTP_SERVER = 'mail.na.nai.com'
# CC_EMAIL = '_267625@McAfee.com;'
# TO_EMAIL = 'DL MFE Labs Engineering - URL False positive monitor <_2dc6a0@McAfee.com>'
TO_EMAIL = 'avi_mehenwal@mcafee.com'    # Testing
CC_EMAIL = 'avi_mehenwal@mcafee.com'    # Testing

# Logging
FORMAT = '%(asctime)-15s %(message)s'
# logging.basicConfig(filename='myapp.log', level=logging.INFO, format=FORMAT)
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

start_time = datetime.datetime.now()

if __name__ != '__main__':
    raise ImportError('ERROR: This script cannot be imported.')


def email(from_email, to_email, cc_email, subject, contents, smtp_server, attachments=None):
    logging.info('Sending email to: %s' % to_email)
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Cc'] = cc_email

    html = MIMEText(contents, 'html')
    logging.warning(html)

    msg.attach(html)
    # return None

    for file_name in attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_name, "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_name))
        msg.attach(part)

    try:
        # print(msg)
        server = smtplib.SMTP(smtp_server)
        server.set_debuglevel(1)
        server.sendmail(from_email, to_email.split(';'), "%s" % msg)
        server.quit()
    except:
        logging.error('Unable to send email.')
        raise
    logging.info('Email sent!')


def main():
    SUPPORTED_CLIENTS = 'sdkclient'
    parser = argparse.ArgumentParser(description='GTI Cloud URL lookup utility.')
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-fp',
                       help="""Run False positive tests""",
                       dest='fp',
                       action='store_true', )
    group.add_argument('-fn',
                       help="""Run False negative tests""",
                       dest='fn',
                       action='store_true', )
    group.add_argument('-ms',
                       help="""Run Mcafee secure tests""",
                       dest='ms',
                       action='store_true', )
    parser.add_argument('-c', '--client',
                        help="""Client to use for lookups(default-sdkclient) - %s""" % ','.join(SUPPORTED_CLIENTS),
                        dest='client',
                        action='store', )
    parser.add_argument('input_file',
                        help='Text input file with list of urls', )
    parser.add_argument('-e', '--email',
                        help="""Email recipient""",
                        dest='email',
                        action='store', )
    parser.add_argument('-t', '--threads',
                        help="""No of threads 0 < t < 512""",
                        dest='threads',
                        action='store',
                        type=int)
    # Adding new CLI argument for url reviewed
    group.add_argument('-r',
                        help="""Update reviewed URLs in database""",
                        dest='reviewed',
                        action='store_true',
                        )

    opts = parser.parse_args()
    print(opts)

    if opts.threads:
        threads = int(opts.threads)
    else:
        threads = 10
        logging.warning('Default of threads = %s' % threads)
    if threads < 1 or threads > 512:
        logging.error('Enter number of threads via -t ')
        exit(10)

    if not opts.email:
        logging.warning('Email will not be sent.')

    if not opts.client:
        logging.warning('Using sdkclient for lookups.')
        opts.client = 'sdkclient'

    subject = subject_suffix = summary = detail_report = ''
    email_text = []

    if opts.fp:
        looker = URLCloudLooker(threads, test_type='fp', client=opts.client)
        subject = 'False positive monitoring report'
        subject_suffix, summary, detail_report = looker.fn_fp_tests(opts.input_file)
        # html_summary = looker._get_html_summary()

    if opts.fn:
        looker = URLCloudLooker(threads, test_type='fp', client=opts.client)
        subject = 'False negative  monitoring report'
        subject_suffix, summary, detail_report = looker.fn_fp_tests(opts.input_file)
        # html_summary = looker._get_html_summary()

    if opts.ms:
        looker = URLCloudLooker(threads, test_type='ms', client=opts.client)
        looker.mcafee_secure_tests(opts.input_file)

    if opts.email:
        subject = 'URL - %s %s' % (subject, subject_suffix)
        body = summary + '\n' + '<br>Time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds + \
            '\n<br>Note: This list contains alexa top 15,000 domains. ' + \
            '<br><br>--Automated email.<br>WEB QA TEAM<br>DL MFE Labs Engineering - Web QA <_267625@McAfee.com>'

        ## print('\n'.join(detail_report))
        email(FROM_EMAIL, TO_EMAIL, CC_EMAIL, subject, body, SMTP_SERVER, attachments=['result.xlsx'])
        logging.info('time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds)

    if opts.reviewed :
        logging.info('Updating reviewed URLs')
        looker = URLCloudLooker(threads, test_type='fp', client=opts.client)
        looker.set_reviewed(opts.input_file)
        print('Done')

if __name__ == '__main__':
    try:
        main()
    finally:
        logging.info('time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds)
    exit(0)

## NOTE:
# [avimehenwal] reviewed url option usage
# python false_positive_script.py -r input_file
# where input_file is the url file (one per line) which have been reviewed by web analysts


# BENCHMARKS :
## 10th-October-2014
# 5000 urls -> 10 hours
## 13th-October-2014
# 20 urls -> 1 minute
## 14th-October-2014
# 5000 urls -> 6 minutes