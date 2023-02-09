"""
Static file locations
*********************
"""

from path import Path


class PROP:
    application = Path('/opt/sftools/conf/application.properties')
    harvester = Path('/opt/sftools/conf/harvester.properties')
    jboss_ejb_client = Path('/opt/sftools/conf/jboss-ejb-client.properties')
    catserver = Path('/opt/sftools/conf/catserver.properties')
    fetcher = Path('/opt/sftools/conf/fetcher.properties')
    gti_cloud_client = Path('/opt/sftools/conf/gti_cloud_client.properties')
    tiered_harvest = Path('/opt/sftools/conf/tieredharvest.properties')
    urldb_queue = Path('/opt/sftools/conf/urldb_queue.properties')
    security_workflow = Path('/opt/sftools/conf/SecurityAutoratingWorkflow.properties')
    regex_security_workflow = Path('/opt/sftools/conf/regex_securityworkflow.properties')
    virustotal_workflow= Path('/opt/sftools/conf/VirusTotalWorkflow.properties')
    drtuf_workflow=Path('/opt/sftools/conf/DRTUFWorkflow.properties')
    markmonitor_workflow=Path('/opt/sftools/conf/MarkMornitorWorkflow.properties')
    VXVault_workflow=Path('/opt/sftools/conf/VXVault.properties')
    MWGMalwareDirect_workflow=Path('/opt/sftools/conf/MWGMalwareDirect.properties')
    FaceBookBlackList_workflow=Path('/opt/sftools/conf/FaceBookBlackListWorkflow.properties')
    Mayhemic_workflow=Path('/opt/sftools/conf/MayhemicHarvestWorkflow.properties')
    saasmalware_workflow=Path('/opt/sftools/conf/SaasMalwareWorkflow.properties')
    cleanmxworkflow=Path('/opt/sftools/conf/CleanMxVirusWorkflow.properties')
    Drsprescan_workflow=Path('/opt/sftools/conf/Drsprescanworkflow.properties')
    Drsblack_workflow=Path('/opt/sftools/conf/DRSBlackworkflow.properties')
    MRTUF_workflow=Path('/opt/sftools/conf/MRTUFHarvestworkflow.properties')
    Abusix_workflow=Path('/opt/sftools/conf/AbusixHarvestworkflow.properties')
    MalwareDomainList=Path('/opt/sftools/conf/MalwareDomainListHarvestWorkflow.properties')
    APWG=Path('/opt/sftools/conf/APWGHarvestWorkflow.properties')
    DenyHost=Path('/opt/sftools/conf/DenyHostHarvestWorkflow.properties')
    QuantcastUncatURLs=Path('/opt/sftools/conf/QuantcastUncatURLs.properties')
    MrgEffitasHarvestWorkflow=Path('/opt/sftools/conf/MrgEffitasHarvestWorkflow.properties')
    QihooHarvestWorkflow=Path('/opt/sftools/conf/QihooHarvestWorkflow.properties')
    NetCraftHarvestWorkflow=Path('/opt/sftools/conf/NetCraftHarvestWorkflow.properties')
    RepperHarvestWorkflow=Path('/opt/sftools/conf/RepperHarvestWorkflow.properties')
    RaidenParsedharvestWorkflow =Path('/opt/sftools/conf/RaidenparsedHarvestWorkflow.properties')
    PhishtankScrapperharvestWorkflow=Path('/opt/sftools/conf/PhishtankScrapperharvestWorkflow.properties')
    BitDefenderHarvestWorkflow=Path('/opt/sftools/conf/BitDefenderharvestWorkflow.properties')


class Others:
    log4j = Path('/opt/sftools/conf/log4j.xml')
    odbc = Path('/etc/odbc.ini')
    freetds = Path('/etc/freetds/freetds.conf')
    jboss_standalone = Path('/opt/sftools/java/jboss7/standalone/configuration/standalone-full-ha.xml')


class Misc:
    sanity_urls = Path('/opt/sftools/conf/sanityUrls.txt')
    dms_sanity = Path('/opt/sftools/conf/dms_sanity_file.txt')


class SH:
    # list build
    build_lists = Path('/usr2/smartfilter/build/build_lists.sh')
    blist_script = Path('/usr2/smartfilter/build/blist_script.sh')
    elist_script = Path('/usr2/smartfilter/build/elist_script.sh')
    setup_build_script = Path('/usr2/smartfilter/build/setup_build_script.sh')
    # canonicalizer
    url_canon_client = Path('/opt/sftools/bin/UrlCanonClient.sh')
    url_normalizer = Path('/opt/sftools/bin/TestNormalize.sh')
    # top sites
    run_alexa_persist = Path('/opt/sftools/bin/run_alexa_persist.sh')
    top_sites_client = Path('/opt/sftools/bin/TopSitesClient.sh')
    popular_url_scrapper = Path('/opt/sftools/bin/run_PopularSitesUrlScraper.sh')
    # java agent/prevalence
    start_agent = Path('/opt/sftools/bin/StartAgent.sh')
    prevalence_client = Path('/opt/sftools/bin/PrevalenceClient.sh ')
    # harvester drivers
    harvester = Path('/opt/sftools/bin/start_harvester.sh')
    content_extractor_driver = Path('/opt/sftools/bin/ContentExtractorDriver.sh')
    content_parser_driver = Path('/opt/sftools/bin/ContentParserDriver.sh')
    source_adapter_driver = Path('/opt/sftools/bin/GenericSourceAdapterDriver.sh')
    content_provider_driver = Path('/opt/sftools/bin/ContentProviderDriver.sh ')
    # security workflow
    security_workflow_agent = Path('/opt/sftools/bin/StartSecurityWorkflowAgent.sh')
    urlexpander_client= Path('/opt/sftools/bin/UrlExpanderClient.sh')



class BIN:
    # agents
    tman = Path('/usr2/smartfilter/dbtools/tman')
    wrman = Path('/usr2/smartfilter/dbtools/wrman')
    crua = Path('/usr2/smartfilter/dbtools/crua')
    cbman = Path('/usr2/smartfilter/dbtools/cbman')
    wrua = Path('/usr2/smartfilter/dbtools/wrua')
    dman = Path('/usr2/smartfilter/dbtools/dman')
    nrua = Path('/usr2/smartfilter/dbtools/nrua')
    shutdown_agent = Path('/usr2/smartfilter/dbtools/shutdown_agent')
    vman = Path('/usr2/smartfilter/dbtools/vman')

    # list build
    sfimport = Path('/usr2/smartfilter/import/sfimport')
    build_lists = Path('/usr2/smartfilter/build/build_lists')
    sfv4checkurl = Path('/usr2/smartfilter/build/sfv4checkurl')
    sfv4diff = Path('/usr2/smartfilter/build/sfv4diff')
    sfv4merge = Path('/usr2/smartfilter/build/sfv4merge')


class LOG:
    harvester = Path('/opt/sftools/log/harvester.log')
    agents = Path('/opt/sftools/log/agents.log')
    scorer = Path('/opt/sftools/log/scorers.log')
    common = Path('/opt/sftools/log/common.log')
    jboss = Path('/opt/sftools/log/jboss.log')
    guvnor = Path('/opt/sftools/log/guvnor.log')
    catserver = Path('/opt/sftools/log/catserver.log')
    thflogs = Path('/opt/sftools/log/thflogs.log')
    domip = Path('/opt/sftools/log/domip.log')
    gti_client = Path('/opt/sftools/log/gti_client.log')
    puppet = Path('/opt/sftools/log/puppet.log')
    drools = Path('/opt/sftools/log/drools.log')
    # Build Log Files
    build_log = Path('/usr2/smartfilter/build/logs/')
    build_master = Path('/usr2/smartfilter/build/logs/master')
    build_migt_xl = Path('/usr2/smartfilter/build/logs/migt/xl')
    build_migt_ts = Path('/usr2/smartfilter/build/logs/migt/ts')


class LIST:
    """ Build Lists  """
    build_agent = 'SFBUILD'
    ts = Path('/usr2/smartfilter/build/ts')
    xl = Path('/usr2/smartfilter/build/xl')
    ts_db = Path('/usr2/smartfilter/build/ts/tsdatabase')
    xl_db = Path('/usr2/smartfilter/build/xl/sfcontrol')
    ts_sanity = Path('/usr2/smartfilter/build/ts/TS4.3_URLS.txt')
    xl_sanity = Path('/usr2/smartfilter/build/xl/XL4.3_URLS.txt')


class DIR:
    """ Commonly used directories """
    urldb_json_dir = Path('/data/urldb/')

    provider_sourceDir=Path('/opt/sftools/scorers/securityworkflow/src')
    provider_workingDir= Path('/opt/sftools/scorers/securityworkflow/working')
    provider_archiveDir=Path('/opt/sftools/scorers/securityworkflow/archive')

    provider_workingDirDRTUF=Path('/data/workflows/harvester/DRTUF/working')
    provider_archiveDirDRTUF=Path('/data/workflows/harvester/DRTUF/archive')
    provider_sourceDirDRTUF=Path('/data/harvesters/urlharvest_trusted')
    provider_errorDirDRTUF=Path('/data/workflows/harvester/DRTUF/error')

    provider_workingDirMarkMonitor=Path('/data/workflows/harvester/MarkMonitor/working')
    provider_archiveDirMarkMonitor=Path('/data/workflows/harvester/MarkMonitor/archive')
    provider_sourceDirMarkMonitor=Path('/data/workflows/harvester/MarkMonitor/source')
    provider_errorDirMarkMonitor=Path('/data/workflows/harvester/MarkMonitor/error')

    provider_workingDirVXVault=Path('/data/workflows/harvester/VXVault/working')
    provider_archiveDirVXVault=Path('/data/workflows/harvester/VXVault/archive')
    provider_downloadDirVXVault=Path('/data/workflows/harvester/VXVault/download')
    provider_errorDirVXVault=Path('/data/workflows/harvester/VXVault/error')

    provider_errorDirMWGMalware=Path('/data/workflows/harvester/MWGMalwareDirect/error')
    provider_archiveDirMWGMalware=Path('/data/workflows/harvester/MWGMalwareDirect/archive')
    provider_workingDirMWGMalware=Path('/data/workflows/harvester/MWGMalwareDirect/working')
    provider_sourceDirMWGMalware=Path('/data/foundViruses/')

    provider_workingDirFBB=Path('/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/working')
    provider_archiveDirFBB=Path('/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/archive')
    provider_downloadDirFBB=Path('/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/download')
    provider_errorDirFBB=Path('/data/webcache/workflows/harvesters/FaceBookBlackListHarvestWorkflow/error')

    provider_archiveDirMayhemic=Path('/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/archive')
    provider_downloadDirMayhemic=Path('/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/download')
    provider_errorDirMayhemic=Path('/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/error')
    provider_workingDirMayhemic=Path('/data/webcache/workflows/harvesters/MayhemicHarvestWorkflow/working')

    provider_workingDirSaaSmalware=Path('//data/workflows/harvester/SaasMalware/working')
    provider_archiveDirSaaSmalware=Path('/data/workflows/harvester/SaasMalware/archive')
    provider_sourceDirSaaSmalware=Path('/data/workflows/harvester/data/wps_virus')
    provider_errorDirSaaSmalware=Path('/data/workflows/harvester/SaasMalware/error')

    provider_workingDirVirus=Path('/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/working')
    provider_archiveDirVirus=Path('/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/archive')
    provider_sourceDirVirus=Path('/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/src')
    provider_errorDirVirus=Path('/data/mapr/data/tsweb/harvesters/VirusTotalHarvester/error')

    provider_workingDirCleanMxVirus=Path('/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/working')
    provider_archiveDirCleanMxVirus=Path('/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/archive')
    provider_sourceDirCleanMxVirus=Path('/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/source')
    provider_errorDirCleanMxVirus=Path('/data/webcache/workflows/harvesters/CleanMxVirusHarvestWorkflow/error')

    provider_workingDirDRSPrescan=Path('/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/working')
    provider_archiveDirDRSPrescan=Path('/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/archive')
    provider_sourceDirDRSPrescan=Path('/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/source')
    provider_errorDirDRSPrescan=Path('/data/webcache/workflows/harvesters/DRSprescanHarvestWorkflow/error')

    provider_workingDirDRSBlack=Path('/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/working')
    provider_archiveDirDRSBlack=Path('/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/archive')
    provider_sourceDirDRSBlack=Path('/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/source')
    provider_errorDirDRSBlack=Path('/data/webcache/workflows/harvesters/DRSBlackHarvestWorkflow/error')

    provider_workingDirMRTUF=Path('/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/working')
    provider_archiveDirMRTUF=Path('/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/archive')
    provider_sourceDirMRTUF=Path('/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/source')
    provider_errorDirMRTUF=Path('/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/error')

    provider_workingDirAbusix=Path('/data/webcache/workflows/harvesters/AbusixHarvestWorkflow/working')
    provider_archiveDirAbusix=Path('/data/webcache/workflows/harvesters/AbusixHarvestWorkflow/archive')
    provider_sourceDirAbusix=Path('/data/webcache/workflows/harvesters/AbusixHarvestWorkflow/source')
    provider_errorDirAbusix=Path('/data/webcache/workflows/harvesters/AbusixHarvestWorkflow/error')

    provider_workingDirMalwareDomainList=Path('/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/working')
    provider_archiveDirMalwareDomainList=Path('/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/archive')
    provider_sourceDirMalwareDomainList=Path('/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/source')
    provider_errorDirMalwareDomainList=Path('/data/webcache/workflows/harvesters/MalwareDomainListHarvestWorkflow/error')

    provider_workingDirAPWG=Path('/data/webcache/workflows/harvesters/APWGHarvestWorkflow/working')
    provider_archiveDirAPWG=Path('/data/webcache/workflows/harvesters/APWGHarvestWorkflow/archive')
    provider_sourceDirAPWG=Path('/data/webcache/workflows/harvesters/APWGHarvestWorkflow/source')
    provider_errorDirAPWG=Path('/data/webcache/workflows/harvesters/APWGHarvestWorkflow/error')

    provider_workingDirDenyHost=Path('/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/working')
    provider_archiveDirDenyHost=Path('/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/archive')
    provider_sourceDirDenyHost=Path('/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/source')
    provider_errorDirDenyHost=Path('/data/webcache/workflows/harvesters/DenyhostsHarvestWorkflow/error')

    provider_workingDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/working')
    provider_archiveDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/archive')
    provider_sourceDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/source')
    provider_errorDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/error')

    provider_workingDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/working')
    provider_archiveDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/archive')
    provider_sourceDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/source')
    provider_errorDirQuantcastUncatURLs=Path('/data/workflows/harvester/QuantcastUncatURLsHarvestWorkflow/error')

    provider_workingDirMrgEffitasHarvestWorkflow=Path('/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/working')
    provider_archiveDirMrgEffitasHarvestWorkflow=Path('/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/archive')
    provider_sourceDirMrgEffitasHarvestWorkflow=Path('/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/source')
    provider_errorDirMrgEffitasHarvestWorkflow=Path('/data/webcache/workflows/harvesters/MrgEffitasHarvestWorkflow/error')

    provider_workingDirQihooHarvestWorkflow=Path('/data/webcache/workflows/harvesters/QihooHarvestWorkflow/working')
    provider_archiveDirQihooHarvestWorkflow=Path('/data/webcache/workflows/harvesters/QihooHarvestWorkflow/archive')
    provider_sourceDirQihooHarvestWorkflow=Path('/data/webcache/workflows/harvesters/QihooHarvestWorkflow/source')
    provider_errorDirQihooHarvestWorkflow=Path('/data/webcache/workflows/harvesters/QihooHarvestWorkflow/error')

    provider_workingDirNetCraft=Path('/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/working')
    provider_archiveDirNetCraft=Path('/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/archive')
    provider_sourceDirNetCraft=Path('/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/source')
    provider_errorDirNetCraft=Path('/data/webcache/workflows/harvesters/NetcraftHarvestWorkflow/error')

    provider_sourceDirRaidenparsed=Path('/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/raiden/urls_parsed')
    provider_workingDirRaidenParsed=Path('/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/working')
    provider_archiveDirRaidenparsed=Path('/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/archive')
    provider_errorDirRaidenparsed=Path('/data/webcache/workflows/harvesters/RaidenParsedHarvestWorkflow/error')

    provider_sourceDirPhishtankScrapper=Path('/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/source')
    provider_workingDirPhishtankScrapper=Path('/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/working')
    provider_archiveDirPhishtankScrapper=Path('/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/archive')
    provider_errorDirPhishtankScrapper=Path('/data/webcache/workflows/harvesters/PhishtankScraperHarvestWorkflow/error')

    provider_sourceDirBitDefender=Path('/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/source')
    provider_workingDirBitDefender=Path('/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/working')
    provider_archiveDirBitDefender=Path('/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/archive')
    provider_errorDirBitDefender=Path('/data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/error')

    provider_sourceDirRepper=Path('/data/mapr/data/tsweb/harvesters/repper/result/')
    provider_workingDirRepper=Path('/data/webcache/workflows/harvesters/RepperHarvestWorkflow/working')
    provider_archiveDirRepper=Path('/data/webcache/workflows/harvesters/RepperHarvestWorkflow/archive')
    provider_errorDirRepper=Path('/data/webcache/workflows/harvesters/RepperHarvestWorkflow/error')
