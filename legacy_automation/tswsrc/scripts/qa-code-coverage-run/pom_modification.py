__author__ = 'avimehenwal'

import re
import os

append = '''  <profiles>
    <profile>
        <id>instrument</id>
        <properties>
            <final.name>wsr-instrumented</final.name>
        </properties>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.codehaus.mojo</groupId>
                    <artifactId>cobertura-maven-plugin</artifactId>
                    <configuration>
                    </configuration>
                    <executions>
                        <execution>
                            <id>instrument-code</id>
                            <phase>process-classes</phase>
                            <goals>
                                <goal>instrument</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <artifactId>maven-source-plugin</artifactId>
                    <executions>
                        <execution>
                            <id>attach-sources</id>
                            <goals>
                                <goal>jar</goal>
                            </goals>
                        </execution>
                    </executions>
                    <inherited>true</inherited>
                </plugin>
            </plugins>
        </build>
    </profile>
  </profiles>
</project>
'''

path = '/home/toolguy/code-coverage/WEB_R007/tsw/tools/system'
file = 'pom.xml'
tmp_file = '~pom.xml'

with open(os.path.join(path, file), "r", encoding = "utf-8") as pom:
    pattern1 = "<goal>cobertura</goal>"
    pattern2 = "</project>"
    rep1 = "<!-- <goal>cobertura</goal> -->"
    rep2 = ""
    pomfile = pom.read()
    # print(pomfile)
    # print(type(pomfile))
    sub1 = re.sub(pattern1, rep1, pomfile ,count=1)
    new = re.sub(pattern2, rep2, sub1, count=1)
    print(new)
    print(type(new))

    # comparision
    if pomfile is new:
        print('No substitution Done : Bad Luck')
    else:
        with open(os.path.join(path, tmp_file), "w", encoding = "utf-8") as pom_new:
            print('Substitution done')
            print(pom_new.write(new + append))

            pom_new.seek(0, os.SEEK_END)
            size_pom_new = pom_new.tell()
            pom.seek(0, os.SEEK_END)
            size_pom = pom.tell()
            print('File Size pom_new = %s'%(size_pom_new))
            print('File Size pom = %s'%(size_pom))

if size_pom_new > size_pom:
    # RENAMING
    print('Removing [%s] [%s]'%(path, file)
    os.remove(os.path.join(path, file))
    os.rename(os.path.join(path, tmp_file), os.path.join(path, file))
    print('Files Renamed')

# END
