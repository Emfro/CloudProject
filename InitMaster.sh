#!/bin/bash
source openrc_source.sh
python InitScript.py create Master master
FLOATING_IP=`cat floating_ip.txt`
echo 'sleeping 20 secs'
sleep 20
while ! ping -c1 $FLOATING_IP &>/dev/null; do echo $FLOATING_IP; done
sleep 10
scp -o "StrictHostKeyChecking no" -i ~/.ssh/id_rsa floating_ip.txt ubuntu@$FLOATING_IP:/home/ubuntu/
ssh -o "StrictHostKeyChecking no" -i ~/.ssh/id_rsa ubuntu@$FLOATING_IP 'bash -s' < setupMaster.sh