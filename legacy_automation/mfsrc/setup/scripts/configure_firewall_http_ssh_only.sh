#!/bin/sh
##########################
####  Setup Firewall  ####
##########################

#### Open port 80 and 22
# DNS, SSL are commented out!

echo "cat <<EOF > /etc/sysconfig/iptables
# iptables modified by mf script
# Firewall configuration written by system-config-firewall
# Manual customization of this file is not recommended.
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
# ssh
-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
# dns
#-A INPUT -p udp -m state --state NEW -m udp --dport 53 -j ACCEPT
# ssl
#-A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
#http
-A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
EOF
" | sudo -s

sudo /etc/init.d/iptables restart
