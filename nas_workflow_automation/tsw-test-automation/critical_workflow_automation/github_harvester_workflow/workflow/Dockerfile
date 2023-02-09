FROM centos:5.11
# TODO: set R_HOME=/usr/lib64/R and LIBRARY_PATH=/usr/lib64/R/lib

# Create users, keeping current UIDs and GIDs
RUN groupadd -g 521 toolguy\
    && useradd -u 519 -g 521 toolguy\
    && groupadd -g 502 sfcontrol\
    && useradd -u 502 -g 502 sfcontrol\
    && groupadd -g 504 smartfilter
# copy repos
RUN rm /etc/yum.repos.d/*
COPY yum-repos/* /etc/yum.repos.d/

RUN yum -y update && \
# These ones exit with non-fatal post-install errors
    yum -y install jdk mysql-connector-odbc;\
# Downgrade libselinux or we get a clash between 32 and 64 bits versions
    yum -y downgrade libselinux &&\
# Also install puppet before as yum fails at install order here
    yum -y install puppet;\
    yum -y install wsr-sacore-java wsr-core R python-simplejson curl &&\
# Install R randomForest library for DRTUF
    R -e "install.packages(\"randomForest\", repos=\"http://lib.stat.cmu.edu/R/CRAN\")" &&\
# clean up
    yum -y clean all

#RUN echo 'export R_HOME=/usr/lib64/R' >> /home/toolguy/.bashrc
#RUN . /home/toolguy/.bashrc && source /home/toolguy/.bashrc

RUN mkdir -p /data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/src
RUN mkdir -p /data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/working
RUN mkdir -p /data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/archive
RUN mkdir -p /data/webcache/workflows/harvesters/GithubCommitsHarvestWorkflow/error
RUN mkdir -p /data/harvesters/urlharvest_trusted_model
RUN mkdir -p /data/webcache/notFoundUrlsInSampleDBDest/src
RUN mkdir -p /data/webcache/maxmind/
RUN mkdir -p /data/urldb
# Copy library to run R from java
COPY libjri.so /opt/sftools/lib/
COPY sftools_conf/* /opt/sftools/conf/
COPY rules/* /opt/sftools/rules/
COPY sftools_sanity/* /opt/sftools/sanity/
COPY webcache_maxmind/* /data/webcache/maxmind/
# copy DB config
COPY odbc*.ini /etc/
COPY freetds.conf /etc/freetds/freetds.conf


#USER toolguy
ENV R_HOME /usr/lib64/R

# Copy and install latest RPMs
# COPY rpms/* /tmp/
#RUN rpm -Uvh /tmp/wsr-*.rpm

COPY log4j.xml /opt/sftools/conf/log4j.xml

# Make sure puppet is stopped
RUN /etc/init.d/puppet stop; exit 0
