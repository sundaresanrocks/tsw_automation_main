import subprocess
import sys

filename = sys.argv[1]
urls = open(filename, 'r').readlines()

for url in urls:
    exec_cmd = '/opt/sftools/bin/AutoratingURLSubmitter.sh tsstgas01 ' + url
    spobj = subprocess.Popen(exec_cmd, stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                shell=True)
    stdout, stderr = spobj.communicate()
    print(stdout)
    print(stderr)