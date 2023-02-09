FROM centos:7

# Create users, keeping current UIDs and GIDs
RUN groupadd -g 521 toolguy\
    && useradd -u 519 -g 521 toolguy\
    && groupadd -g 502 sfcontrol\
    && useradd -u 502 -g 502 sfcontrol\
    && groupadd -g 504 smartfilter

RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install python-pip gcc python-devel && \
    yum -y clean all

COPY github_crawler/* /home/toolguy/github_crawler/
COPY run_crawler.sh /home/toolguy/github_crawler/
RUN pip install -r /home/toolguy/github_crawler/requirements.txt
