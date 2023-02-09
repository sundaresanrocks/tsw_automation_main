"""
=========================================================
Libraries and configurations required for Customer Ticketing System 
=========================================================
"""
__author__ = 'Anurag'
import logging
from libx.process import ShellExecutor as ShellExecutor
from lib.exceptions import StyleException

class TicketingLib:
    
    ticketing_bin = "/usr2/smartfilter/dbtools/run_ticket_status.pl"
    ui_executor = "http://tsqauitest.wsrlab:4444/wd/hub"
    
    
    @staticmethod
    def updater(status=None, listtype=None):
        """
        Runs Updater.
        Status can be new, open
        list type can be xl or ts
        """
        if status is None and listtype is None:
            raise StyleException("Provide status or listtype information")
        cmd = TicketingLib.ticketing_bin
        if listtype is None:
            cmd = cmd + ' --updater --' + status
        else:
            cmd = cmd + ' --updater --listtype ' + listtype
        
        logging.info('Executing ' + cmd)
        stdout,stderr = ShellExecutor.run_wait_standalone(cmd)
        logging.info(stdout)
        logging.info(stderr)
        return stdout,stderr

    @staticmethod
    def delinquent(status, time, email_to):
        """
        Runs reporter delinquent
        status can be open/reviewed
        time is in hours
        email_to is madatory
        """
        cmd = TicketingLib.ticketing_bin+" --reporter --delinquent --dstatus "+status+" --dhours "+str(time)+" --dto_email "+email_to
        logging.info('Executing ' + cmd)
        stdout,stderr = ShellExecutor.run_wait_standalone(cmd)
        logging.info(stdout)
        logging.info(stderr)
        return stdout,stderr
