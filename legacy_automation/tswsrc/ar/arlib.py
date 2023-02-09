"""Sanity functions , others
"""

import os

from lib.db.mssql import *
from lib.exceptions import TestFailure
import runtime
from libx.xml2obj import Xml2Obj


class Check():
    """This class has function to check key value in file
    """
    def property_check ( self , system , absolute_path , expected_property , expected_value ):
        """This function checks values for properties in file
        """
        
        # getting the file name to put in sandbox folder by exact name
        file_name = ( absolute_path.split('/') )[-1]
        local_file = os.getcwd() + ( '/%s' %file_name )

        #getting file from the remote system
        ssh = runtime.get_ssh ( system ,user='root',password='xdr5tgb')
        ssh.get ( absolute_path , local_file )

        #testing the expected value for the expected property
        fp = open( local_file , 'r' )
        for line in fp.readlines():
            if not ( line.startswith('#') or line.startswith('\n')) and '=' in line:
                key,value = line.split ( '=' )
                key = key.strip()
                value = ( value.split('\n') ) [0]
                if ( key in expected_property ):
                    index = expected_property.index ( '%s' %key )
                    if ( value.strip() == expected_value [ index ].strip() ):
                        logging.info ( 'The value for %s is %s as expected' % ( expected_property , expected_value ) )
                    else:
                        raise TestFailure ( 'The value for %s is %s. \n Expected Value is %s ' % ( expected_property [ index ] , value , expected_value [ index ] ) )
        fp.close()

    def property_check_in_standalone_xml ( self , system , absolute_path ):
        """This function checks the hierarchy of the standalone-full.xml plus calls the function to verify entries
        """

        
        
        # getting the file name to put in sandbox folder by exact name
        file_name = ( absolute_path.split('/') )[-1]
        file = os.getcwd() + ( '/%s' %file_name )
        logging.info ( file )

        #getting file from the remote system
        ssh = runtime.get_ssh ( system , user='toolguy',password='xdr5tgb' )
        ssh.get ( absolute_path , file )
           
        parser = Xml2Obj()
        root = parser.Parse(file)

        # The reason for iterating through the nodes is to make sure that the xml schema is also proper

        for profile_node in root.children:
            if profile_node.name == 'profile':
                for subsystem_node in profile_node.children:
                    if subsystem_node.name == 'subsystem':
                        for datasources_node in subsystem_node.children:
                            if datasources_node.name == 'datasources':
                                for xa_datasources_node in datasources_node.children:
                                    if xa_datasources_node.name == 'xa-datasource':
                                        if xa_datasources_node.getAttribute('jndi-name') == 'java:jboss/datasources/MSSQLXADS_U2':
                                            self.check_db_details(xa_datasources_node , 'U2')
                                        elif xa_datasources_node.getAttribute('jndi-name') == 'java:jboss/datasources/MSSQLXADS_D2':
                                            self.check_db_details(xa_datasources_node , 'D2')
                                        elif xa_datasources_node.getAttribute('jndi-name') == 'java:jboss/datasources/MSSQLXADS_R2':
                                            self.check_db_details(xa_datasources_node , 'R2')
                                            
        
    def check_db_details(self , xa_datasources_node , db ):
        """This function checks the Database and Server Name for U2 , D2 and R2 databases
        """
        
        import re
        p = re.compile("^\s*")
        for xa_datasources_property in xa_datasources_node.children:
            if xa_datasources_property.getAttribute('name') == 'ServerName':
                for m in p.finditer( xa_datasources_property.getData() ):
                    end = m.end()
                    logging.info ( xa_datasources_property.getData()[ end  : ] )
                    logging.info('Envcon host >>> ' + runtime.DB.D2_host)
                    if not ( xa_datasources_property.getData()[ end  : ] ) == runtime.DB.D2_host:
                        raise TestFailure ('Expected %s , but Found %s' % ( runtime.DB.D2_host , xa_datasources_property.getData()[ end  : ] ) )
            if xa_datasources_property.getAttribute('name') == 'DatabaseName':
                for m in p.finditer( xa_datasources_property.getData() ):
                    end = m.end()
                    logging.info ( xa_datasources_property.getData()[ end  : ] )
                    if not ( xa_datasources_property.getData()[ end  : ] ) == '%s' %db:
                        raise TestFailure ('Expected %s , but Found %s' % ( db , xa_datasources_property.getData()[ end  : ] ) )

    def property_check_in_procman_xml ( self , system , absolute_path ):
        """This function checks the hierarchy of the standalone-full.xml plus calls the function to verify entries
        """
        
        # getting the file name to put in sandbox folder by exact name
        file_name = ( absolute_path.split('/') )[-1]
        file = os.getcwd() + ( '/%s' %file_name )
        logging.info( file )

        #getting file from the remote system
        ssh = runtime.get_ssh ( system , 'toolguy' )
        ssh.get ( absolute_path , file )
           
        parser = Xml2Obj()
        root = parser.Parse(file)
        for process_node in root.children:
            if process_node.name == 'process':
                if process_node.getAttribute('name') == 'wfa':
                    logging.warning (process_node.getAttribute('path'))


class Validate:
    """This class have functions to validate the patterns in the file or string
    """
    def validate ( self , system , absolute_path , expected_output ) :
        """ Function to match patterns in a file
        """
        file = absolute_path
        #finding the expected strings in file
        logging.info ( ' Checking for the expected outputs in %s ' % file )

        fp = open ( file , 'r' )
        content = fp.read().replace('\n' , '\t')
        for pattern in expected_output:
            logging.info ( ' Finding Pattern : %s' % pattern )
            lower = content.find( pattern )
            if lower == -1:
                logging.error ( 'NOT FOUND : Pattern %s in %s' % ( pattern , file ) )
                raise TestFailure ( 'NOT FOUND : Pattern %s in %s' % ( pattern , file ) )
            else:
                logging.info ( 'FOUND Pattern %s found in %s' % ( pattern , file ) )

        fp.close()

    def get_scorer_data_for_url ( self , system , absolute_path , url_id , url ):
        """ Function which fetches data in the log related to a specific url
        """

        import os
        data = ''''''
        # getting the file name to put in sandbox folder by exact name
        file_name = ( absolute_path.split('/') )[-1]
        file = os.getcwd() + ( '/%s' %file_name )
        logging.warning ( file )

        #getting file from the remote system ( if the file size is big , you can delete the file after the required checks )
        ssh = runtime.get_ssh ( system , 'toolguy' )
        ssh.get ( absolute_path , file )

        #index holders
        lower = -1
        lower1 = -1

        fp = open ( file , 'r' )
        content = fp.readlines()
        for line in content:
            ''''''
            lower = line.find(':%s' % url)
            if lower == -1:
                lower1 = line.find('urlId=%s' %url_id)
            if ( lower != -1 or lower1 != -1):
                data += line
        fp.close()
        return data
    
    def validate_in_scorer_data ( self , data , expected_output ):
        """Function to search for pattern in data
        """
        for pattern in expected_output:
            logging.info ( ' Finding Pattern : %s' % pattern )
            lower = data.find( pattern )
            if lower == -1:
                logging.error ( 'NOT FOUND : Pattern %s ' % ( pattern ) )
                raise TestFailure ( 'NOT FOUND : Pattern %s ' % ( pattern ) )
            else:
                logging.info ( 'FOUND : Pattern %s ' % ( pattern ) )

    def get_file ( self , system , absolute_path ):
        """Getting file from remote system and putting it in sandbox folder
        """


