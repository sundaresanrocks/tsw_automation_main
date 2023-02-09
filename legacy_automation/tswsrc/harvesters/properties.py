from libx.pyjavaproperties import Properties
from collections import OrderedDict
__author__ = 'manoj'
import runtime


def _add_content_provider(prop_dict, content_provider, harvester_name):
    """
    Define the default content provider dict here
    :param content_provider:
    :return:
    """
    prop_dict["%s.ContentProvider.className" % harvester_name] = 'com.securecomputing.sftools.harvester' + \
                                                          '.contentProviders.%s' % content_provider
    if content_provider == 'FileContentProvider':
        prop_dict['FileContentProvider.sourceDir'] = runtime.data_path + \
                                                     '/tsw/harvesters/driver/content_providers/server_root'
        prop_dict['FileContentProvider.fileRegex'] = '.*'


def _add_content_parser(prop_dict, content_parser, harvester_name):
    """
    Define the default content parser dict here
    :param content_parser:
    :return:
    """
    prop_dict['%s.ContentParser.className' % harvester_name] = 'com.securecomputing.sftools.harvester.contentParsers.%s' % content_parser

    if content_parser == 'CSVContentParser':
        prop_dict['CSVContentParser.maxNumberOfColumns'] = '1'
        prop_dict['CSVContentParser.fieldSeparator'] = ','
        prop_dict['CSVContentParser.column.1'] = 'url'

    if content_parser == 'RSSContentParser':
        prop_dict['RSSContentParser.regex'] = '^URL: (.*?), IP Address: (.*?), Country: (.*?), ASN: (.*?), MD5: (.*?)$'
        prop_dict['RSSContentParser.numberOfFields'] = '5'
        prop_dict['RSSContentParser.field.1'] = 'url'
        prop_dict['RSSContentParser.field.2'] = 'ip_address'
        prop_dict['RSSContentParser.field.3'] = 'country'
        prop_dict['RSSContentParser.field.4'] = 'asn'
        prop_dict['RSSContentParser.field.5'] = 'md5'

    if content_parser == 'XMLContentParser':
        prop_dict['XMLContentParser.minLines'] = '0'
        prop_dict['XMLContentParser.root'] = 'entry'
        prop_dict['XMLContentParser.key'] = 'url'
        prop_dict['XMLContentParser.prefix'] = 'Prefix'
        prop_dict['XMLContentParser.required'] = 'url,count'

        prop_dict['Prefix.url'] = 'url'
        prop_dict['Prefix.count'] = 'count'

    if content_parser == 'JSONContentParser':
        prop_dict['%s.JSONContentParser.prefix' % harvester_name] = 'JSONContentParser.keyname'
        prop_dict['JSONContentParser.required'] = 'url,date,key'
        prop_dict['JSONContentParser.root'] = 'links'
        prop_dict['JSONContentParser.key'] = 'url'

        prop_dict['JSONContentParser.keyname.url'] = 'url'
        prop_dict['JSONContentParser.keyname.key'] = 'key'
        prop_dict['JSONContentParser.keyname.status'] = 'status'
        prop_dict['JSONContentParser.keyname.source'] = 'source'
        prop_dict['JSONContentParser.keyname.date'] = 'date'


def quality_properties(harvester_name='Quality',
                       properties_as_dict=None,
                       content_provider=None,
                       content_parser=None,
                       write_to_file=False):

    prop_dict = OrderedDict(
        {'scheduler.HarvesterName': harvester_name,
         'sourceRegex': '\\.txt$',
         'ruleBaseNames': 'tsw.harvester.qa.%s.dsltest' % harvester_name,
         'useLocalRuleFile': 'y',
         'localRuleFileBaseDirectory': runtime.data_path + '/tsw/harvesters/%s/rules/' % harvester_name,
         'PersistEventData': 'false'}
    )
    if properties_as_dict:
        prop_dict.update(properties_as_dict)

    _add_content_provider(prop_dict, content_provider, harvester_name)
    _add_content_parser(prop_dict, content_parser, harvester_name)

    prop = Properties(prop_dict)
    if write_to_file:
        prop.write_to_file(write_to_file)
    return prop
