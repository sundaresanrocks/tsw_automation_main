"""
==================
Default Properties
==================
"""

import runtime
from path import Path
from libx.pyjavaproperties import Properties


def __default_prop_actions(prop_object, write_file_name=None, update_dict=None, delete_key_list=None):
    if update_dict:
        prop_object.update(update_dict)

    if write_file_name:
        with open(write_file_name, 'w', encoding='UTF-8') as fpw:
            prop_object.store(fpw)
        if not Path(write_file_name).isfile():
            raise FileNotFoundError(write_file_name)

    if delete_key_list:
        if not isinstance(delete_key_list, list):
            raise TypeError('delete_keys_list must be list. found: %s' % type(delete_key_list))
        for key_to_delete in delete_key_list:
            del prop_object[key_to_delete]


def set_prop_jboss_ejb_client(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for jboss ejb client properties
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['remote.connectionprovider.create.options.org.xnio.Options.SSL_ENABLED'] = 'false'
    prop['remote.connections'] = 'default'
    prop['remote.connection.default.host'] = runtime.AppServer.host
    prop['remote.connection.default.port'] = '4447'
    prop['remote.connection.default.connect.options.org.xnio.Options.SASL_POLICY_NOANONYMOUS'] = 'false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.jboss_ejb_client if write_file_bool else None)
    return prop

def prop_catserver(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for catserver.properties
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['Port'] = '4006'
    prop['ClassicPort'] = 'default'
    prop['XLList'] = '/data/build/staging/xl/sfcontrol'
    prop['TSList'] = '/data/build/staging/ts/tsdatabase'
    prop['StatsInterval'] = '300000'
    prop['SN'] = 'SF12-3456-7890-1234'
    prop['ProductName'] = 'CatServer'
    prop['ProductVersion'] = '1'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.catserver if write_file_bool else None)
    return prop


def set_prop_application(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    # Database connections
    prop['mssql.telemetry.host'] = runtime.DB.T_host
    prop['mssql.telemetry.db'] = runtime.DB.T_name
    prop['mssql.telemetry.username'] = runtime.DB.T_user
    prop['mssql.telemetry.password'] = runtime.DB.T_pass
    prop['mssql.telemetry.telemetryTables'] = runtime.DB.T_telemetry_tables

    prop['mssql.u2.host'] = runtime.DB.U2_host
    prop['mssql.u2.db'] = 'U2'
    prop['mssql.u2.username'] = runtime.DB.U2_user
    prop['mssql.u2.password'] = runtime.DB.U2_pass

    prop['mssql.d2.host'] = runtime.DB.D2_host
    prop['mssql.d2.db'] = 'D2'
    prop['mssql.d2.username'] = runtime.DB.D2_user
    prop['mssql.d2.password'] = runtime.DB.D2_pass

    prop['mssql.r2.host'] = runtime.DB.R2_host
    prop['mssql.r2.db'] = 'R2'
    prop['mssql.r2.username'] = runtime.DB.R2_user
    prop['mssql.r2.password'] = runtime.DB.R2_pass

    # mongo DB properties
    prop['mongodb.topsites.host'] = runtime.Mongo.TopSites.host
    prop['mongodb.topsites.port'] = str(runtime.Mongo.TopSites.port)
    prop['mongodb.topsites.db'] = runtime.Mongo.TopSites.dbname
    prop['mongodb.topsites.collection'] = runtime.Mongo.TopSites.collection
    #prop['mongodb.topsites.username'] = runtime.Mongo.TopSites.user
    #prop['mongodb.topsites.password'] = runtime.Mongo.TopSites.passwd


    prop['mongodb.dwa.host'] = runtime.Mongo.DOMIP.host
    prop['mongodb.dwa.port'] = str(runtime.Mongo.DOMIP.port)
    prop['mongodb.dwa.database'] = runtime.Mongo.DOMIP.dbname
    prop['mongodb.dwa.collection'] = runtime.Mongo.DOMIP.table

    prop['mongodb.urldb.host'] = runtime.Mongo.URLDB.host
    prop['mongodb.urldb.port'] = str(runtime.Mongo.URLDB.port)
    prop['mongodb.urldb.db'] = runtime.Mongo.URLDB.dbname

    prop['autorating.mongohost'] = runtime.Mongo.host
    prop['autorating.mongodb'] = runtime.Mongo.auto_rating_db
    prop['autorating.mongoport'] = str(runtime.Mongo.port)
    prop['autorating.mongocollection'] = runtime.Mongo.auto_rating_collection
    prop['autorating.skipResetQueue'] = 'false'
    prop['autorating.securityCategories'] = 'ap,an,be,cc,dl,hk,ms,ph,pu,qd,sy,sd,pc,su,ml'

    # sample DB properties
    prop['SampleDBDatabase.driver'] = 'net.sourceforge.jtds.jdbc.Driver'
    prop['SampleDBDatabase.database'] = 'jdbc:jtds:sqlserver://sampledbreadonly.corp.avertlabs.internal/Sample'
    prop['SampleDBDatabase.user'] = 'svcacct-wsr'
    prop['SampleDBDatabase.password'] = 'K9B@all9!'

    # sanity files
    prop['sanityFile'] =  '/opt/sftools/conf/sanityUrls.txt'
    prop['dmsSanityFactGenerator.dmsSanityFile'] = '/opt/sftools/conf/dms_sanity_file.txt'

    # catserver
    prop['catserver.host'] = runtime.cat_server_host
    prop['catserver.port'] = str(runtime.cat_server_port)

    # JMS Utils Settings
    prop['jmsQueueUsername'] = 'toolguy'
    prop['jmsQueuePassword'] = '1qazse4'

    # URLDB
    prop['urldb.file.destination'] = '/data/urldb'
    prop['urldb.contributorReport.printLargest'] = 'false'

    # URLDB shortener-expander
    prop['urldb.expandShortenedUrls'] = 'true'
    prop['cloudPatterns.inputFile']='/home/toolguy/workspace/QA-CI-HIL/res/urldb/regex_security_workflow/regexes.txt'
    # Do Not Crawl Domains File
    prop['dncDomainsFile']='/opt/sftools/conf/dnc_domains_file.txt'
    # Drtuf
    prop['drtuf.modelFile']='/data/harvesters/urlharvest_trusted_model/exe.model.rf_tr_1week_latest.rdata'
    prop['drtufFactGenerator.supportedUrlRegex.1']='.*\\.exe.*'


    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.application if write_file_bool else None)

    return prop


def prop_prevalence_agent(*, write_file_name=None, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for prevalence agent
    :param write_file_name: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.PrevalenceProvider'
    prop['consumer.classname'] = 'com.mcafee.tsw.agent.consumer.PrevalenceConsumer'
    prop['consumer.threadcount'] = '1'
    prop['worker.classname.1'] = 'com.mcafee.tsw.agent.worker.PrevalenceWorker'
    prop['worker.threadcount.1'] = '10'
    prop['agent.getlock'] = 'true'
    prop['agent.name'] = 'Prevalence'
    prop['verbose'] = 'false'
    prop['prevalence.batchsize'] = '10'
    prop['agent.appserver'] = runtime.AppServer.host
    prop['agent.updateProcessHistory'] = 'false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=write_file_name)

    return prop


def prop_publish_agent(*, write_file_name=None, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for publish prevalence agent
    :param write_file_name: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.PublishPrevalenceProvider'
    prop['verbose'] = 'true'
    prop['agent.appserver'] = runtime.AppServer.host
    prop['agent.name'] = 'Publish'
    prop['agent.polltime'] = '30000'
    prop['agent.getlock'] = 'false'

    prop['agent.publish.safeMode'] = 'false'

    prop['agent.publish.xlGreenPercent'] = '0'
    prop['agent.publish.xlGreyPercent'] = '0'
    prop['agent.publish.xlYellowPercent'] = '0'
    prop['agent.publish.xlRedPercent'] = '0'

    prop['agent.publish.xlNumberUrls'] = '1600000'
    prop['agent.publish.xlAllowedUpdates'] = '100000000'
    prop['agent.publish.tsAllowedUpdates'] = '1000000000'

    prop['agent.publish.xlEnsureCatPublish1'] = 'bl  bu  mk'
    prop['agent.publish.xlEnsureCatPublish2'] = 'bl  bu  fi  hl  it  nw  os  sn'
    prop['agent.publish.tsRemoveCategoryThreshold1'] = 'ms|30'
    prop['agent.publish.tsTrimIsGenIps'] = 'true'
    prop['agent.publish.tsTrimIsGenIpAge'] = '90'
    prop['agent.publish.xlMinDomainPrevalence'] = '0'
    prop['agent.publish.tsEnsurePublishedCat.1'] = 'mr'
    prop['agent.publish.tsEnsurePublishedDays'] = '10'
    
    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=write_file_name)

    return prop

def prop_harvester(*, harvester_name = 'APWG', write_file_name=None, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for publish prevalence agent
    :param write_file_name: writes to a file
    :param update_dict: updates the Properties with new values
    :return: property dictionary
    """
    prop = Properties()

    prop['scheduler.HarvesterName'] = harvester_name

    if harvester_name == 'APWG':
        #prop['APWG.mode'] = 'delta'
        #prop['APWG.mode.delta.filename'] = 'APWG_latest.txt'

        prop['APWG.ContentProvider.className'] = 'com.securecomputing.sftools.harvester.contentProviders.FileContentProvider'
        prop['harvesterSourceDir'] = '/tmp/test_auto/harvester/APWG_src/'
        prop['FileContentProvider.sourceDir'] = '/tmp/test_auto/harvester/APWG_src/'
        
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop['RegexReplacePreprocessor.match.1'] = '"3D'
        prop['RegexReplacePreprocessor.replace.1'] = '"'
        prop['RegexReplacePreprocessor.match.2'] = ',"([^"]*)"([^"]*)",'
        prop['RegexReplacePreprocessor.replace.2'] = ',"$1%22$2",'

        prop['APWG.ContentParser.className'] = 'com.securecomputing.sftools.harvester.contentParsers.CSVContentParser'
        prop['CSVContentParser.maxNumberOfColumns'] = '6'
        prop['CSVContentParser.fieldSeparator'] = ','
        prop['CSVContentParser.column.1'] = 'target'
        prop['CSVContentParser.column.2'] = 'date_added'
        prop['CSVContentParser.column.3'] = 'score'
        prop['CSVContentParser.column.4'] = 'url'
        prop['CSVContentParser.column.5'] = 'url_encoded'
        prop['CSVContentParser.column.6'] = 'type'

        prop['PersistEventData'] = 'true'
        prop['TierOneSourceType'] = 'harvester'
        prop['GlobalMetaData.status'] = 'false'
        prop['APWG.sfimportEnabled'] = 'false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=write_file_name)

    return prop

def prop_securityworkflow_VirusTotal(*,  write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/src'
    prop['provider.workingDir']='/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/working'
    prop['provider.archiveDir']='/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/archive'
    prop['provider.errorDir']='/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/error'
    #prop['provider.recognizedExtensions']='.pdf,.scr,.exe,.mp3'
    prop['provider.enabledHeartbeat']='true'
    prop['provider.heartrate']='500'

    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['parser.classname']='com.mcafee.tsw.parser.JSONPathFileParser'
    prop['JSONPathFileParser.objectSelector']='$.[*]'
    prop['JSONPathFileParser.objectFieldSelector.url']='$.url'
    prop['JSONPathFileParser.objectFieldSelector.timestamp']='$.timestamp'
    prop['JSONPathFileParser.objectFieldSelector.score']='$.score'
    prop['JSONPathFileParser.objectFieldSelector.positives']='$.positives'
    prop['JSONPathFileParser.objectFieldSelector.scans']='$.scans'
    prop['JSONPathFileParser.customParser.scans']='com.mcafee.tsw.parser.VirusTotalScanFieldParser'
    prop['JSONPathFileParser.objectFieldSelector.first_seen']='$.first_seen'
    prop['JSONPathFileParser.childSelector']='.'

    # UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Info
    prop['verbose']='true'
    prop['agent.name']='VirusTotalWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.virustotal_workflow if write_file_bool else None)


def prop_security_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.SecurityWorkflowProvider'
    prop['provider.enableHeartbeat'] = 'true'
    prop['provider.heartrate'] = '500'
    prop['provider.limit'] = '1500'
    prop['workflow.batchsize'] = '751'


    #prop['worker.classname.1'] = 'com.mcafee.tsw.agent.worker.SampleDBWorker'
    #prop['worker.threadcount.1'] = '5'
    #prop['sampledb.properties.path'] = '/opt/sftools/conf/securityAutorating_scorer.properties'
    #prop['sampledb.enableHeartbeat'] = 'true'
    #prop['sampledb.heartrate'] = '500'


    ##prop['worker.classname.2'] = 'com.mcafee.tsw.agent.worker.GoogleSafeBrowseWorker'
    ##prop['worker.threadcount.2'] = '1'
    #prop['safebrowse.properties.path'] = '/opt/sftools/conf/securityAutorating_scorer.properties'
    #prop['safebrowse.enableHeartbeat'] = 'true'
    #prop['safebrowse.heartrate'] = '500'

    #prop['worker.classname.2'] = 'com.mcafee.tsw.agent.worker.WebFetcherWorker'
    #prop['worker.threadcount.2'] = '13'
    #prop['fetcher.properties.path'] = '/opt/sftools/conf/securityAutorating_fetcher.properties'
    #prop['fetcher.enableHeartbeat'] = 'true'
    #prop['fetcher.heartrate'] = '500'

    # FactGenerator worker. Spawns multiple fact generators
    #prop['worker.classname.3']='com.mcafee.tsw.agent.worker.FactGeneratorWorker'
    #prop['worker.threadcount.3']= '5'
    #prop['factGenerator.properties.path']= '/opt/sftools/conf/factGenerator.properties'
    #Factgenerators
    #prop['factgenerator.classname.1']= 'com.intel.labs.factGenerator.TopSitesFactGenerator'
    #prop['factgenerator.classname.2']= 'com.intel.labs.factGenerator.CatServerFactGenerator'
    #prop['factgenerator.classname.3']= 'com.intel.labs.factGenerator.DmsSanityFactGenerator'
    #prop['factgenerator.classname.4']= 'com.intel.labs.factGenerator.DrtufFactGenerator'
    #prop['factgenerator.classname.5']= 'com.intel.labs.factGenerator.UrlComponentFactGenerator'
    #prop['factgenerator.classname.6']= 'com.intel.labs.factGenerator.GeolocationFactGenerator'


    prop['consumer.classname'] = 'com.mcafee.tsw.agent.consumer.SecurityWorkflowsGenericConsumer'
    prop['consumer.enableHearbeat'] = 'true'
    prop['consumer.heartrate'] = '100'

    prop['verbose'] = 'true'
    prop['agent.name'] = 'AutoSecurityWorkflow'
    prop['agent.sendToUrlDB'] = 'true'
    prop['agent.getlock'] = 'false'
    prop['agent.updateProcessHistory'] = 'false'




    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.security_workflow if write_file_bool else None)

    return prop


def prop_harvester_prop(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['guvnorserver'] = runtime.guvnor_server_host
    prop['guvnorusername'] = 'tsw'
    prop['guvnorpassword'] = 'tsw'
    prop['appserver.hostname'] = runtime.AppServer.host
    prop['DmsSanityCheck.sanityFile'] = '/opt/sftools/sanity/dms_sanity_file.txt'
    prop['AlexaSanityCheck.sanityFile'] = '/data/harvesters/alexa/alexa_top_1000000.txt'
    prop['harvesterSourceDir'] = '/home/toolguy/anegi/workflow'
    prop['PersistEventData'] = 'false'
    prop['maxFilesToProcess'] = '50'
    prop['catserverHost'] = runtime.cat_server_host
    prop['catserverPort'] = '4006'
    prop['catserverRetryCount'] = '4'
    prop['catserverRetrySleepMS'] = '3000'
    prop['urldb.file.destination'] = '/data/urldb/'
    prop['urldb.file.sizeLimit'] = '1000'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.harvester if write_file_bool else None)

    return prop


def prop_jboss_ejb_client_prop(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['remote.connectionprovider.create.options.org.xnio.Options.SSL_ENABLED'] = 'false'
    prop['remote.connections'] = 'default'
    prop['remote.connection.default.host'] = runtime.AppServer.host
    prop['remote.connection.default.port '] = '4447'
    prop['remote.connection.default.connect.options.org.xnio.Options.SASL_POLICY_NOANONYMOUS'] = 'false'


    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.jboss_ejb_client if write_file_bool else None)

    return prop


def prop_urldb_queue_prop(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for urldb_queue.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()
    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.UrlDBQueueProvider'
    prop['consumer.classname'] = 'com.mcafee.tsw.agent.consumer.UrlDBQueueConsumer'
    prop['worker.classname.1'] = 'com.mcafee.tsw.agent.worker.UrlDBQueueWorker'
    prop['worker.threadcount.1'] = '10'
    prop['verbose'] = 'true'
    prop['agent.name'] = 'URLDBQueueLoader'
    prop['agent.getlock'] = 'false'
    prop['agent.updateProcessHistory'] = 'false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.urldb_queue if write_file_bool else None)

    return prop


def prop_regex_security_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.FileContentWorkProvider'
    prop['provider.sourceDir'] = '/opt/sftools/scorers/securityworkflow/src'
    prop['provider.workingDir'] = '/opt/sftools/scorers/securityworkflow/working'
    prop['provider.archiveDir'] = '/opt/sftools/scorers/securityworkflow/archive'
    prop['provider.parser.classname'] = 'com.mcafee.tsw.parser.CsvFileParser'
    prop['CsvParser.column.1'] = 'url'
    prop['consumer.classname'] = 'com.mcafee.tsw.agent.consumer.FactOutputConsumer'
    prop['worker.classname.1'] = 'com.mcafee.tsw.agent.worker.FactGeneratorWorker'
    prop['worker.threadcount.1'] = '1'

    prop['factgenerator.classname.1'] = 'com.intel.labs.factGenerator.CloudPatternsFactGenerator'
    #prop['cloudPatterns.inputFile'] = '/home/toolguy/workspace/QA-CI-HIL/res/urldb/regex_security_workflow/regexes.txt'
    prop['verbose'] = 'true'
    prop['PersistEventData'] = 'true'
    prop['agent.name'] = 'SecurityWorkflow'
    prop['agent.getlock'] = 'false'
    prop['agent.updateProcessHistory'] = 'false'


    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.regex_security_workflow if write_file_bool else None)

    return prop

def prop_drtuf_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir'] = '/data/harvesters/urlharvest_trusted'
    prop['provider.workingDir'] = '/data/workflows/harvester/DRTUF/working'
    prop['provider.errorDir']='/data/workflows/harvester/DRTUF/error'
    prop['provider.archiveDir'] = '/data/workflows/harvester/DRTUF/archive'
    prop['provider.sourceRegex'] = 'drtuf_*.*'

    # Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'

    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.NVPairFileParser'
    prop['NVPairFileParser.nameValSeperator']==''
    prop['NVPairFileParser.skipBadLine']='true'
    prop['NVPairFileParser.delimiter']='\t'
    prop['parser.keepFiles']='true'
    prop['parser.skipParsedFiles']='true'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

    prop['verbose']='true'
    prop['agent.name']='DRTUFWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.drtuf_workflow if write_file_bool else None)

    return prop

def prop_markmonitor_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname'] = 'com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceRegex']='2*.txt'
    prop['provider.sourceDir'] = '/data/workflows/harvester/MarkMonitor/source'
    prop['provider.workingDir'] = '/data/workflows/harvester/MarkMonitor/working'
    prop['provider.archiveDir']='/data/workflows/harvester/MarkMonitor/archive'
    prop['provider.errorDir'] = '/data/workflows/harvester/MarkMonitor/error'
    prop['provider.heartrate']='2'
    prop['provider.limit']='1'
    prop['provider.batchsize']='2'
    prop['provider.enabledHeartbeat']='false'

    # Worker 1 Settings

    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.PreprocessorWorker'
    prop['worker.threadcount.1']='1'
    prop['Preprocessor.count']='1'
    prop['Preprocessor.1.className']='com.mcafee.tsw.preprocessor.RegexReplacePreprocessor'
    prop['RegexReplacePreprocessor.match.1']='\t+'
    prop['RegexReplacePreprocessor.match.1']='\t'

    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.2']='1'

    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.NVPairFileParser'
    prop['NVPairFileParser.nameValSeperator']==''
    prop['NVPairFileParser.skipBadLine']='true'
    prop['NVPairFileParser.delimiter']='\\t'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

    prop['verbose']='true'
    prop['agent.name']='MarkMonitorWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.markmonitor_workflow if write_file_bool else None)

    return prop

def prop_VXVault_Workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/workflows/harvester/VXVault/download'
    prop['provider.errorDir']='/data/workflows/harvester/VXVault/error'
    prop['provider.archiveDir']='/data/workflows/harvester/VXVault/archive'
    prop['provider.workingDir']='/data/workflows/harvester/VXVault/working'
    prop['provider.parser.classname']='com.mcafee.tsw.parser.HtmlTableFileParser'

    # Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'

    # UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

    # Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.HtmlTableFileParser'
    prop['parser.skipParsedFiles']='true'
    prop['HtmlTableFileParser.tableNumber']='1'
    prop['HtmlTableFileParser.skipRows']='1'
    prop['HtmlTableFileParser.column.2']='url'
    prop['HtmlTableFileParser.column.3']='md5'

    # Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    # Info
    prop['verbose']='true'
    prop['agent.name']='VxVaultHarvestWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.VXVault_workflow if write_file_bool else None)


def prop_MWGMalwareDirect_Workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()
    # Worker 1 Settings

    # Provider Settings
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/foundViruses/'
    prop['provider.workingDir']='/data/workflows/harvester/MWGMalwareDirect/working'
    prop['provider.errorDir']='/data/workflows/harvester/MWGMalwareDirect/error'
    prop['provider.archiveDir']='/data/workflows/harvester/MWGMalwareDirect/archive'

    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.PreprocessorWorker'
    prop['worker.threadcount.1']='1'
    prop['Preprocessor.count']='1'
    prop['Preprocessor.1.className']='com.mcafee.tsw.preprocessor.RegexReplacePreprocessor'
    prop['Preprocessor.1.className']='com.mcafee.tsw.preprocessor.RegexReplacePreprocessor'
    prop['RegexReplacePreprocessor.match.1']='\\\023'
    prop['RegexReplacePreprocessor.replace.1']='%13'

    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.2']='1'
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'
    prop['CsvParser.maxNumberOfColumns']='4'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.column.1']='timestamp'
    prop['CsvParser.column.2']='client_ip'
    prop['CsvParser.column.3']='detection_string'
    prop['CsvParser.column.4']='url'
    prop['parser.keepFiles']='true'
    prop['parser.skipParsedFiles']='true'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

# Info
    prop['verbose']='true'
    prop['agent.name']='MWGMalwareDirectHarvesterWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.MWGMalwareDirect_workflow if write_file_bool else None)

def prop_FacebookBlackList_Workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    """
    Returns Properties object for application.properties contents
    :param write_file_bool: writes to a file
    :param update_dict: updates the Properties with new values
    :return:
    """
    prop = Properties()

    # Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/download'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/error'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/working'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

    # Parse the file
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['parser.classname']='com.mcafee.tsw.parser.JSONPathFileParser'
    prop['JSONPathFileParser.objectSelector']='$.data.[*]'
    prop['JSONPathFileParser.objectFieldSelector.url']='$.raw_indicator'
    prop['JSONPathFileParser.objectFieldSelector.status']='$.status'
    prop['JSONPathFileParser.objectFieldSelector.added_on']='$.added_on'
    prop['JSONPathFileParser.objectFieldSelector.type']='$.type'
    prop['JSONPathFileParser.childSelector']='.'

    # Tracked facts
    prop['FactTracker.added_on']='next_query_time,com.mcafee.tsw.agent.facttracker.NextToLastFactTracker'
    prop['FactTracker.fileStore']='/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/facts.properties'


    # Write JSON data to be uploaded to UrlDB
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

    # Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

    # Info
    prop['verbose']='true'
    prop['agent.name']='FaceBookBlackListHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    # Worker 1 Settings
    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.FaceBookBlackList_workflow if write_file_bool else None)


def prop_Mayhemic_Workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

     # Provider details
    prop = Properties()
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/archive'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/download'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/error'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/working'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

    # Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

    # Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.skipRowCount']='21'
    prop['CsvParser.maxNumberOfColumns']='4'
    prop['CsvParser.column.1']='url'
    prop['CsvParser.column.2']='mayhemic_reason'
    prop['CsvParser.column.3']='mayhemic_source'
    prop['CsvParser.column.4']='mayhemic_score'

# parser.keepFiles=true
# parser.skipParsedFiles=true

# URL expander
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='2'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info
#verbose=true

    prop['agent.name']='MayhemicHarvestWorflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.Mayhemic_workflow if write_file_bool else None)


def prop_SaasMalware_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):
    # Provider Settings
    prop = Properties()
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceRegex']='2*.csv'
    prop['provider.sourceDir']='/data/workflows/harvester/data/wps_virus'
    prop['provider.workingDir']='/data/workflows/harvester/SaasMalware/working'
    prop['provider.errorDir']='/data/workflows/harvester/SaasMalware/error'
    prop['provider.archiveDir']='/data/workflows/harvester/SaasMalware/archive'
    prop['provider.parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'

# Worker Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'
    prop['CsvParser.fieldSeparator']=','
    prop['CsvParser.skipRowCount']='0'
    prop['CsvParser.maxNumberOfColumns']='2'
    prop['CsvParser.column.1']='url'
    prop['CsvParser.column.2']='company_and_detection'


# Worker - Expand shortened URLs
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='1'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Canonicalize and sanitize URLs
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlStandardizerWorker'
    prop['worker.threadcount.3']='1'

# Worker - Write JSON data to be uploaded to UrlDB
    prop['worker.classname.4']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.4']='1'

    # Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

# Info
    prop['verbose']='true'
    prop['agent.name']='SaasMalwareWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.saasmalware_workflow if write_file_bool else None)

def prop_CleanMxVirus_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

        # Provider
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/source'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/working'
    prop['provider.errorDir']= '/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/archive'
    prop['provider.parser.classname']='com.mcafee.tsw.parser.XMLFileParser'
    prop['provider.heartrate']='2'
    prop['provider.limit']='1'
    prop['provider.batchsize']='2'
# Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.PreprocessorWorker'
    prop['worker.threadcount.1']='1'
    prop['Preprocessor.count']='1'
    prop['Preprocessor.1.className']='com.mcafee.tsw.preprocessor.RegexReplacePreprocessor'
    prop['RegexReplacePreprocessor.match.1']='\\017'
    prop['RegexReplacePreprocessor.replace.1']='%0FM'
# Convert vt_score sting of "x/y (z.d%)" to "z", not it truncates instead of rounding.
    prop['RegexReplacePreprocessor.match.2']='<vt_score>([0-9]+)/([0-9])+.*\\(([0-9]*).*?%\\).*</vt_score>'
    prop['RegexReplacePreprocessor.replace.2']='<vt_score>$3</vt_score><vt_hits>$1</vt_hits>'

    prop['RegexReplacePreprocessor.match.3']='</url>]]></url>'
    prop['RegexReplacePreprocessor.replace.3']='</url>'

    prop['RegexReplacePreprocessor.match.4']='</url>/]]></url>'
    prop['RegexReplacePreprocessor.replace.4']='</url>'

    prop['RegexReplacePreprocessor.match.5']=']]>]]></url>'
    prop['RegexReplacePreprocessor.replace.5']=']]></url>'

# Convert missing vt_scores to 0
    prop['RegexReplacePreprocessor.match.6']='<vt_score></vt_score>'
    prop['RegexReplacePreprocessor.replace.6']='<vt_score>0</vt_score>'


# Worker 2 Settings
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.2']='1'
#Worker 3 Settings
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.XMLFileParser'
    prop['XMLFileParser.prefix']='XMLFileParser.xmltag'
    prop['XMLFileParser.required']='url,response'
    prop['XMLFileParser.root']='entry'
    prop['XMLFileParser.key']='url'

    prop['XMLFileParser.xmltag.url']='url'
    prop['XMLFileParser.xmltag.line']='line'
    prop['XMLFileParser.xmltag.id']='id'
    prop['XMLFileParser.xmltag.first']='first'
    prop['XMLFileParser.xmltag.last']='last'
    prop['XMLFileParser.xmltag.md5']='md5'
    prop['XMLFileParser.xmltag.virustotal']='virustotal'
    prop['XMLFileParser.xmltag.vt_score']='vt_score'
    prop['XMLFileParser.xmltag.vt_hits']='vt_hits'
    prop['XMLFileParser.xmltag.scanner']='scanner'
    prop['XMLFileParser.xmltag.virusname']='virusname'
    prop['XMLFileParser.xmltag.recent']='recent'
    prop['XMLFileParser.xmltag.response']='response'
    prop['XMLFileParser.xmltag.ip']='ip'
    prop['XMLFileParser.xmltag.as']='as'
    prop['XMLFileParser.xmltag.review']='review'
    prop['XMLFileParser.xmltag.domain']='domain'
    prop['XMLFileParser.xmltag.country']='country'
    prop['XMLFileParser.xmltag.source']='source'
    prop['XMLFileParser.xmltag.email']='email'
    prop['XMLFileParser.xmltag.inetnum']='inetnum'
    prop['XMLFileParser.xmltag.netname']='netname'
    prop['XMLFileParser.xmltag.descr']='descr'
    prop['XMLFileParser.xmltag.ns1']='ns1'
    prop['XMLFileParser.xmltag.ns2']='ns2'
    prop['XMLFileParser.xmltag.ns3']='ns3'
    prop['XMLFileParser.xmltag.ns4']='ns4'
    prop['XMLFileParser.xmltag.ns5']='ns5'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['agent.updateProcessHistory']='false'

# Info
    prop['verbose']='true'
    prop['agent.name']='CleanMxVirusHarvestWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.cleanmxworkflow if write_file_bool else None)

def prop_drsprescan_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider details

    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/archive'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.column.1']='url'

# URL expander
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='2'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info

    prop['agent.name']='DRSprescanHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.Drsprescan_workflow if write_file_bool else None)

def prop_DRSBlack_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider details

    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/archive'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.column.1']='url'

# URL expander
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='2'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info

    prop['agent.name']='DRSBlackHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.Drsblack_workflow if write_file_bool else None)

def prop_MRTUF_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

  # Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/archive'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'
    prop['provider.fileRegex']='^Hashes'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'
    prop['parser.keepFiles']='true'
    prop['CsvParser.maxNumberOfColumns']='7'
    prop['CsvParser.fieldSeparator']=','
    prop['CsvParser.skipRowCount']='1'
    prop['CsvParser.column.1']='change_type'
    prop['CsvParser.column.2']='content_md5'
    prop['CsvParser.column.3']='url'
    prop['CsvParser.column.4']='date_added'
    prop['CsvParser.column.5']='id'
    prop['CsvParser.column.6']='content_classification_name'
    prop['CsvParser.column.7']='content_classification_type'


# Canonicalize and sanitize URLs
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlStandardizerWorker'
    prop['worker.threadcount.2']='1'

# UrlDB upload
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info
    prop['agent.name']='MRTUFHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.MRTUF_workflow if write_file_bool else None)


def prop_MalwareDomianKist_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()
    # Provider details

    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/archive'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

# Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.MalwareDomainListFileParser'
    prop['CsvParser.column.1']='date'
    prop['CsvParser.column.2']='url'
    prop['CsvParser.column.3']='ip'
    prop['CsvParser.column.5']='detection_string'

# URL expander'
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='2'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info
#verbose=true
    prop['agent.name']='MalwareDomainListHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.MalwareDomainList if write_file_bool else None)

def prop_APWGHarvesterWorkflow_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/APWGHarvestWorkflow/source'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/APWGHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/APWGHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/APWGHarvestWorkflow/archive'

# Tracker stuff
    prop['FactTracker.fileStore']='/data/webcache/workflows/harvesters/APWGHarvestWorkflow/facts.tracked'

# Worker 1 - parse the JSON
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser settings
    prop['parser.classname']='com.mcafee.tsw.parser.JSONPathFileParser'
    prop['JSONPathFileParser.objectSelector']='$._embedded.phish.[*]'
    prop['JSONPathFileParser.objectFieldSelector.url']='$.url'
    prop['JSONPathFileParser.objectFieldSelector.APWG_date_discovered']='$.date_discovered'
    prop['JSONPathFileParser.objectFieldSelector.APWG_confidence']='$.confidence_level'
    prop['JSONPathFileParser.objectFieldSelector.APWG_brand']='$.brand'
    prop['JSONPathFileParser.objectFieldSelector.APWG_ip']='$.ip'
    prop['JSONPathFileParser.childSelector']='.'

# Worker 3 - Webpage fetcher
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.WebFetcherWorker'
    prop['worker.threadcount.2']='30'
    prop['fetcher.properties.path']='/opt/sftools/conf/RaptorBeta_Fetcher.properties'
    prop['fetcher.enableHeartbeat']='true'
    prop['fetcher.heartrate']='500'

# Worker 4 - FactGenerator worker. Spawns multiple fact generators.
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.FactGeneratorWorker'
    prop['worker.threadcount.2']='10'
    prop['factGenerator.properties.path']='/opt/sftools/conf/factGenerator.properties'


#Factgenerators
    prop['factgenerator.classname.1']='com.intel.labs.factGenerator.TopSitesFactGenerator'
    prop['factgenerator.classname.2']='com.intel.labs.factGenerator.CatServerFactGenerator'
    prop['factgenerator.classname.5']='com.intel.labs.factGenerator.GeolocationFactGenerator'
    prop['factgenerator.classname.7']='com.intel.labs.factGenerator.U2FactGenerator'

# Worker 8 - Standardize URLs
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlStandardizerWorker'
    prop['worker.threadcount.3']='1'

# Worker 9 - UrlDB upload
    prop['worker.classname.4']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.4']='1'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

# Info
    prop['verbose']='true'
    prop['agent.name']='APWGHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.APWG if write_file_bool else None)


def prop_DenyHostHarvestWorkflow_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/source'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/working'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

# Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.XMLFileParser'
    prop['XMLFileParser.prefix']='XMLFileParser.xmltag'
    prop['XMLFileParser.required']='string'
    prop['XMLFileParser.root']='value'
    prop['XMLFileParser.key']='string'
    prop['XMLFileParser.numSkipRootNodes']='2'

    # The harvest workflow framework expects at least a url field.
    #XMLFileParser.xmltag.string=ip
    prop['XMLFileParser.xmltag.string']='url'

    # Worker 9 - UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'
# Info
    prop['verbose']='true'
    prop['agent.name']='DenyhostsHarvestWorkflow'
    prop['agent.getlock']='false'

    # Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.DenyHost if write_file_bool else None)

def prop_QuantcastUncatURLs_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider Settings
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceRegex']='*.txt'
    prop['provider.sourceDir']='/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/source'
    prop['provider.workingDir']='/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/working'
    prop['provider.errorDir']='/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/archive'
    prop['provider.parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'

# Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'
    prop['CsvParser.maxNumberOfColumns']='1'
    prop['CsvParser.column.1']='url'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'

    # Worker 9 - UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'
# Info
    prop['verbose']='true'
    prop['agent.name']='QuantcastUncatURLsHarvestWorkflow'
    prop['agent.sendToUrlDB']='true'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.QuantcastUncatURLs if write_file_bool else None)


def prop_MrgEffitasHarvestWorkflow_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

# Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/working'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/error'
    prop['provider.fileRegex']='.*.txt$'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['parser.fieldSeparator']='\\t'
    prop['CsvParser.column.1']='url'
    prop['parser.keepFiles']='true'

# URL expander
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='75'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info

    prop['agent.name']='MrgEffitasHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.MrgEffitasHarvestWorkflow if write_file_bool else None)


def prop_QihooHarvestWorkflow_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()
    # Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/QihooHarvestWorkflow/working'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/QihooHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/QihooHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/QihooHarvestWorkflow/error'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Parser
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['parser.fieldSeparator']='\\t'
    prop['CsvParser.column.1']='url'
    prop['parser.keepFiles']='true'

# URL expander
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlExpanderWorker'
    prop['worker.threadcount.2']='75'
    prop['urlExpander.timeout']='2000'
    prop['urlExpander.maxRedirects']='20'

# Write to JSON files for UrlDB queue loader
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Info

    prop['agent.name']='QihooHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.QihooHarvestWorkflow if write_file_bool else None)


def prop_NetCraftHarvest_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider configuration
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/working'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/source'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/error'
# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'
# Worker 1
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
    prop['parser.classname']='com.mcafee.tsw.parser.NetcraftFileParser'

# UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

# Info
    prop['verbose']='true'
    prop['agent.name']='NetcraftHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.NetCraftHarvestWorkflow if write_file_bool else None)


def prop_RepperHarvest_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceRegex']='*_rule_*'
    prop['provider.sourceDir']='/data/mapr/data/tsweb/harvesters/repper/result/'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/RepperHarvestWorkflow/working'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/RepperHarvestWorkflow/archive'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/RepperHarvestWorkflow/error'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'

# Parse the file
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.RepperFileParser'
    prop['parser.keepFiles']='true'
    prop['parser.skipParsedFiles']='true'

# Canonicalize URLs before sending them to UrlDB
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlStandardizerWorker'
    prop['worker.threatcount.2']='3'

# Write JSON data to be uploaded to UrlDB
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'


# Info
    prop['verbose']='true'
    prop['agent.name']='RepperHarvestWorkflow'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.RepperHarvestWorkflow if write_file_bool else None)



def prop_RaidenParsed_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider configuration
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceRegex']='ExportDataParsedLocation*'
    prop['provider.enableHeartbeat']='true'
    prop['provider.heartrate']='500'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/raiden/urls_parsed'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/archive'
    prop['provider.limit']='2'

# Worker 1
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.PreprocessorWorker'
    prop['worker.threadcount.1']='1'
    prop['Preprocessor.count']='1'
    prop['Preprocessor.1.className']='com.mcafee.tsw.preprocessor.RegexReplacePreprocessor'
    prop['RegexReplacePreprocessor.match.1']='http//'
    prop['RegexReplacePreprocessor.replace.1']='http://'
    prop['RegexReplacePreprocessor.match.2']='https//'
    prop['RegexReplacePreprocessor.replace.2']='https://'
    prop['RegexReplacePreprocessor.match.2']='https//'
    prop['RegexReplacePreprocessor.replace.2']='https://'
    prop['RegexReplacePreprocessor.match.4']='tcp://'
    prop['RegexReplacePreprocessor.replace.4']='http://'

# Worker 2
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.2']='10'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.RaidenFileParser'
    prop['parser.keepFiles']='false'
    prop['parser.skipParsedFiles']='false'
    prop['RaidenParser.skipRowCount']='1'
    prop['RaidenParser.maxNumberOfColumns']='5'
    prop['RaidenParser.fieldSeparator']=','
    prop['RaidenParser.column.1']='changeType'
    prop['RaidenParser.column.2']='md5'
    prop['RaidenParser.column.3']='url'
    prop['RaidenParser.column.4']='dateTimeAdded'
    prop['RaidenParser.column.5']='id'

# Work 3 UrlDB upload
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Info
    prop['verbose']='true'
    prop['agent.name']='RaidenParsedHarvestWorkflow'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.RaidenParsedharvestWorkflow if write_file_bool else None)


def prop_PhishTankScrapper_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider configuration
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/source'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/archive'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/working'

# This file sould be automatically created at the first run.  No deploy needed.
    prop['PhishtankScraper.lastPhishtankIdStore']='/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/phishtank.lastid.txt'

# Worker 1 Settings
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['worker.threadcount.1']='1'
# Parser Settings
    prop['parser.classname']='com.mcafee.tsw.parser.HarvesterCSVParser'
    prop['CsvParser.maxNumberOfColumns']='2'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.skipRowCount']='0'
    prop['CsvParser.column.1']='phishtank_id'
    prop['CsvParser.column.2']='url'

# UrlDB upload
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.2']='1'

# Consumer Settings
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Info
    prop['verbose']='true'
    prop['agent.name']='PhishtankScraperHarvestWorkflow'
    prop['agent.getlock']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                           write_file_name=runtime.PROP.PhishtankScrapperharvestWorkflow if write_file_bool else None)

def prop_BitDefender_workflow(*, write_file_bool=True, update_dict=None, delete_key_list=None):

    prop = Properties()

    # Provider details
    prop['provider.classname']='com.mcafee.tsw.agent.provider.FileNameWorkProvider'
    prop['provider.sourceDir']='/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/source'
    prop['provider.workingDir']='/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/working'
    prop['provider.errorDir']='/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/error'
    prop['provider.archiveDir']='/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/archive'

# Parse the file
    prop['worker.classname.1']='com.mcafee.tsw.agent.worker.FileParserWorker'
    prop['parser.classname']='com.mcafee.tsw.parser.CsvFileParser'
    prop['CsvParser.maxNumberOfColumns']='1'
    prop['CsvParser.fieldSeparator']='\\t'
    prop['CsvParser.skipRowCount']='0'
    prop['CsvParser.column.1']='url'

# Clean urls (they come with hxxp instead of http)
    prop['worker.classname.2']='com.mcafee.tsw.agent.worker.UrlStandardizerWorker'

# Write JSON data to be uploaded to UrlDB
    prop['worker.classname.3']='com.mcafee.tsw.agent.worker.UrlDBQueueContributerWorker'
    prop['worker.threadcount.3']='1'

# Consumer
    prop['consumer.classname']='com.mcafee.tsw.agent.consumer.HarvesterConsumer'
    prop['consumer.enableHeartbeat']='true'
    prop['consumer.heartrate']='500'

# Info
    prop['verbose']='true'
    prop['agent.name']='BitDefenderHarvestWorkflow'
    prop['agent.getlock']='false'
    prop['agent.updateProcessHistory']='false'

    __default_prop_actions(prop, update_dict=update_dict, delete_key_list=delete_key_list,
                        write_file_name=runtime.PROP.BitDefenderHarvestWorkflow if write_file_bool else None)

