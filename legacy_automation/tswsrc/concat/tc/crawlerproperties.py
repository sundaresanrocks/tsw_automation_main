"""
===================================
Social Media Crawler Configuration
===================================
"""

import runtime

class CrawlerProperties:
    """
    Specifies the Crawler Executable Location and Various property files to be picked up
    """
   
    config_path=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/social_media_crawler.properties')
    crawler_path='/opt/sftools/bin/run_social_media_spider.sh'
    config_path_07=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/tc_07.properties')
    config_path_14=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/tc_14.properties')
    config_path_19=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/tc_19.properties')
    config_path_21=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/tc_21.properties')
    config_path_end=runtime.data_path.joinpath('/tsw/concat/social_media_crawler/conf/end-end_crawler.properties')
