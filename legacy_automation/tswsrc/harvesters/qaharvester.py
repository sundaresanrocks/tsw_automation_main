from harvesters.harvester_config import HarvesterConfig
import runtime

__author__ = 'manoj'


class HarvesterQuality(HarvesterConfig):
    harvester_name = 'Quality'
    session_owner = 'Quality'

    properties_file = runtime.data_path + '/tsw/harvesters/Quality/Quality.properties'
    working_dir = HarvesterConfig.base_working + 'Quality/working/'
    processed_files = HarvesterConfig.base_working + 'Quality/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)