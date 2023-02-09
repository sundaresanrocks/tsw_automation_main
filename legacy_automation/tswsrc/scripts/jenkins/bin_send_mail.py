"""
================================
Remote email script
================================

Sends email by HTTP GET to a remote machine

"""
import os
import re
import sys
import requests


URL_TMPL = '''http://%(ip)s/tsa/download.php?t=mail&m=yes&j=%(build)s'''
KEY_OPTION = 'Send Email'
KEY_MSG_SENT = 'Message successfully sent!'
KEY_MAIL_TO = 'EMAIL SENT to:'

def curl_to_send_email(ipaddr, email_to):
    """Send email using a remote system"""
        #check if Send Email is set or not
    options = os.environ.get('TSA_RUNTIME_OPTIONS','')
    if not (KEY_OPTION in str(options).split(',')):
        print(('WARNING: Send Email is Disabled via TSA_RUNTIME_OPTIONS.' + ' Unable to send email'))
        sys.exit(0)

        #Get build number
    build_number = os.environ.get('BUILD_NUMBER','')
    if build_number == '':
        print('ERROR: env variable BUILD_NUMBER not found. Unable to send email')
        sys.exit(0)
    if int(build_number) == 0:
        raise ValueError('ERROR: BUILD_NUMBER == 0. Unable to send email')

        #construct the URL
    url = URL_TMPL % {'ip': ipaddr, 
                      'build': build_number}

        #Get the remote object
    robj = requests.get(url)
    if robj.status_code != 200:
        raise EnvironmentError('ERROR: Status Code: %s.' % robj.status_code \
                             + ' Unable to send email')
    html = robj.text

        #Check for SUCCESS
    if not KEY_MSG_SENT in html:
        print('ERROR: Unknown! Unable to send email.')
        sys.exit(0)

        #Print success info
    print(('INFO', KEY_MSG_SENT, 'SUCCESS'))
    print(('INFO', html[html.rfind(KEY_MAIL_TO):]))
    sys.exit(0)



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: bin_send_mail.py <IP of remote machine> <email_to>')
        print('ERROR: Unable to send email')
        sys.exit(0)
    argv = ';'.join(re.findall('"([^"]*)"', ' '.join(sys.argv[2:])))
    print(('INFO Email Settings: ip-', sys.argv[1], 'email list-', argv))
    curl_to_send_email(sys.argv[1], argv)

#os.environ['TSA_RUNTIME_OPTIONS'] = 'Send Email'
#os.environ['BUILD_NUMBER'] = '-43'
#curl_to_send_email('172.19.216.199')
