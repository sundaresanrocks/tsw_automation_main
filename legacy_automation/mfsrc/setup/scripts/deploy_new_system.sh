#!/bin/sh
####################
####  ENV VARS  ####
####################

MF_PROJ_NAME=pp
DJ_PROJ_NAME=mfui
MF_PROJ_PORT=8001
PY3_DIR=/home/$USER/py3/
PY3_VER=3.4.2
V_ENV_DIR="/home/$USER/$MF_PROJ_NAME"env
SRC_DIR="/home/$USER/$MF_PROJ_NAME"src

if [[ $EUID -eq 0 ]]; then
   echo "This script must not be run as root" 1>&2
   echo "Exiting with return code 1" 1>&2
   exit 1
fi


################################
####  Install python 3.4.x  ####
################################

install_py34(){
#### Required packages
sudo yum groupinstall -y development
sudo yum install -y zlib-dev openssl-devel sqlite-devel bzip2-devel

#### Download python
cd ~
mkdir setup
cd setup
wget https://www.python.org/ftp/python/$PY3_VER/Python-$PY3_VER.tgz
tar xzf Python-$PY3_VER.tgz

#### Install Python
cd Python-$PY3_VER
./configure --prefix=$PY3_DIR
make && make altinstall

}

######################
####  supervisord ####
######################

install_supervisord(){

#### install
sudo easy_install supervisor
/usr/bin/echo_supervisord_conf > /etc/supervisord.conf

#### add to crontab
echo "@reboot sudo /usr/bin/supervisord -c /etc/supervisord.conf" > /tmp/supervisord_cron.txt
sudo crontab /tmp/supervisord_cron.txt
rm /tmp/supervisord_cron.txt

#### setup alias
echo "alias zsuctl='sudo supervisorctl -c /etc/supervisord.conf'" >> ~/.bashrc
echo "alias zsurestart='sudo kill supervisord;sudo /usr/bin/supervisord -c /etc/supervisord.conf'" >> ~/.bashrc

}

#######################
####  Setup NGINX  ####
#######################

install_nginx(){
#### Adds repository in cent os 6
echo "Setting up nginx.repo for yum"
echo "cat <<EOF > /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/\$releasever/\$basearch/
gpgcheck=0
enabled=1
EOF
" | sudo -s

echo "Installing nginx"
sudo yum install -y nginx
sudo chkconfig nginx on

echo "Starting nginx"
sudo /etc/init.d/nginx start
}


###############################################################################
###############################  Configurations  ##############################
###############################################################################

#####################
####  virtualenv ####
#####################

install_virtualenv(){

echo "create new virtual environment"
cd ~
/home/$USER/py3/bin/pyvenv-3.4 $V_ENV_DIR
source $V_ENV_DIR/bin/activate
cd $V_ENV_DIR

echo "install gunicorn"
pip install gunicorn

}


create_venv_script(){
#set up environment shell script
cat >/home/$USER/env-$MF_PROJ_NAME.sh <<  EOF

source $V_ENV_DIR/bin/activate
export DJANGO_SETTINGS_MODULE=$MF_PROJ_NAME.settings
export PYTHONPATH="$SRC_DIR":$PYTHONPATH:.

EOF
}

############################################
####  Django environment configuration  ####
############################################
configure_supervisord(){

echo "configure supervisor"
echo "cat <<EOF >> /etc/supervisord.conf

[program:$MF_PROJ_NAME]
command=$V_ENV_DIR/bin/start-$MF_PROJ_NAME-gunicorn.sh
user=$USER
stdout_logfile=$V_ENV_DIR/logs/gunicorn-$MF_PROJ_NAME-supervisor.log   ; Where to write log messages
directory=$V_ENV_DIR
redirect_stderr=true
autostart=true
environment=DJANGO_PROJ_NAME="$MF_PROJ_NAME",DJANGO_VENV_DIR="$V_ENV_DIR"
autorestart=true

EOF
" | sudo -s
}


####################
#### nginx site ####
####################
configure_nginix_site(){
#### Configure nginx
echo "creating nginx virtual file /etc/nginx/conf.d/$MF_PROJ_NAME.conf"
cat <<EOF > /tmp/nginx-$MF_PROJ_NAME.conf
upstream app_server_$MF_PROJ_NAME {
    server localhost:$MF_PROJ_PORT fail_timeout=0;
}

server {
    listen 80;
    server_name `hostname`;

    access_log  /var/log/nginx/$MF_PROJ_NAME-access.log;
    error_log  /var/log/nginx/$MF_PROJ_NAME-error.log info;
    keepalive_timeout 5;

    location /$MF_PROJ_NAME/docs {
        root $SRC_DIR/docs/_build/;
    }
    location / {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$http_host;
        proxy_redirect off;

        if (!-f \$request_filename) {
            proxy_pass http://app_server_${MF_PROJ_NAME};
            break;
        }
    }
}

EOF

sudo cp  /tmp/nginx-$MF_PROJ_NAME.conf /etc/nginx/conf.d/$MF_PROJ_NAME.conf

}

####################
####  gunicorn  ####
####################
create_gunicorn_script(){


cat <<EOF > $V_ENV_DIR/bin/start-$MF_PROJ_NAME-gunicorn.sh
#!/bin/bash
echo \"Starting $DJ_PROJ_NAME as \`whoami\`\"

# Activate the virtual environment
cd $SRC_DIR
echo 'Changed directory to $SRC_DIR'
source $V_ENV_DIR/bin/activate
export PYTHONPATH=$SRC_DIR:$SRC_DIR/dj:.

# Start your Django Unicorn
echo Starting gunicorn..
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $V_ENV_DIR/bin/gunicorn dj.${DJ_PROJ_NAME}.wsgi:application \
  --name dj \
  --workers 4 \
  --user=$USER --group=$USER \
  --log-level=debug \
  --bind=127.0.0.1:$MF_PROJ_PORT
#  --bind=unix: $V_ENV_DIR/run_gunicorn.sock

EOF

#set executable permissions
chmod 0744 $V_ENV_DIR/bin/start-$MF_PROJ_NAME-gunicorn.sh

}



###############################################################################
###################################  Steps  ###################################
###############################################################################

mkdir -p $SRC_DIR
mkdir -p $V_ENV_DIR/logs

echo "Usage"
echo "source this file"
echo "run the desired functions!"
