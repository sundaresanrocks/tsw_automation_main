"""
===========================
rst Documentation Generator
===========================

Generates rsT automodules based on pyproj

"""
# import os
from path import Path
from libx.filex import get_files_in_dir
from collections import OrderedDict

#### Configurations
root_dir = '../'
index_file = 'source/index.rst'

allowed_extensions = ('py')
ignore_prefix = ('tmpmanoj', 'docs')

dirmap = OrderedDict()

dirmap['ar'] = 'ar - autorating tests'
dirmap['build'] = 'build tests'
dirmap['concat'] = 'Content Categorization tests'
dirmap['conf'] = 'Project Specific configurations'
dirmap['dbtools'] = 'dbtools tests'
dirmap['domip'] = 'DOMAIN IP tests'
dirmap['end2end'] = 'End to end tests'
dirmap['harvesters'] = 'Harvester tests'
dirmap['legacy'] = 'legacy tests'
dirmap['lib'] = 'TS Web Systems specific modules'
dirmap['prevalence'] = 'prevalence tests'
dirmap['urldb'] = 'urldb tests'
dirmap['scripts'] = 'scripts'


toc_tree_head = """

    rst/quickstart

    rst/misc

    rst/demo-commands

    rst/setup

"""

toc_tree_tail = """

    rst/code-tips

    rst/code-standards

    rst/code-coverage

    rst/write-unit-tests

    rst/rst/how-to-update-docs

    code-tips

    rst/troubleshooting

"""

#### Constants
TOC_TREE = '.. toctree::\n    :maxdepth: 1\n    :hidden:'
INIT_MARKER = '.. init marker for auto update'
EXIT_MARKER = '.. exit marker for auto update'

#### Initializations

file_list = []



def get_sections(data_l, init_marker=INIT_MARKER, exit_marker=EXIT_MARKER):
    #### Code to compute the init and exit marker position
    line_number = 0
    init_index = exit_index = -1
    for line in data_l:
        line_number += 1
        if (init_index == -1) and (line.strip() == init_marker):
            init_index = line_number
        if (exit_index == -1) and (line.strip() == exit_marker):
            exit_index = line_number
    if (init_index == -1) or (init_index > exit_index):
        raise Exception('MarkerError: Check for init and exit markers')

    return ''.join(index_file_data[:init_index]), ''.join(index_file_data[exit_index - 1:])


def add_to_list(iterator):
    for i in iterator:
        _fname = i.getAttribute('Include')
        file_bool = True
        for _ in ignore_prefix:
            if _fname.startswith('tmpmanoj'):
                file_bool = False
        if _fname.rpartition('.')[2] not in allowed_extensions:
            file_bool = False
        if file_bool:
                file_list.append(_fname.rpartition('.')[0].replace('/', '.'))


# x = xml2obj.Xml2Obj().Parse('k:/gti/gti.pyproj').getElements('ItemGroup')
# for i in x:
#     add_to_list(i.getElements('Compile'))

dirdata = ''


for dir_name in dirmap:
    files = []
    target_dir = Path(root_dir + '/' + dir_name)
    for item in target_dir.walkfiles('*.py'):
        if item.endswith('.py'):
            files.append(str(item)[len(root_dir)+1:-3].replace('/', '.'))
    dirdata += '\n    generated/%s\n' % dir_name
    data = dirmap[dir_name] + '\n' + '=' * len(dirmap[dir_name]) + '\n'
    for fname in files:
        if fname.startswith(dir_name):
            data += '\n.. automodule:: ' + str(fname).replace('/', '.')
            data += '\n    :members:\n'
    file_name = 'source/generated/' + dir_name + '.rst'
    if '/' in file_name:
        Path(file_name.rpartition('/')[0]).makedirs_p()
    with open(file_name, 'w+', newline='\n') as fpw:
        fpw.write(data)


#### Read index file
with open(index_file) as fpr:
    index_file_data = fpr.readlines()

#### Parse head and tail sections
try:
    head_section, tail_section = get_sections(index_file_data)
except Exception as err:
    if 'MarkerError' in err.args[0]:
        print('Check for init and exit markers.\nUnable to update index.rst')
        exit(100)
    else:
        raise

#### Format output data and write to file
data = u'{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(head_section, TOC_TREE, toc_tree_head, str(dirdata),
                                              toc_tree_tail, tail_section)
#todo: remove the comments
with open(index_file, 'w+', newline='\n') as fpw:
    fpw.write(data)
print(dirdata)
