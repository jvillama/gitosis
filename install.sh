#!/bin/sh
#git clone git@github.com:jvillama/gitosis.git
#cd gitosis
#sudo apt-get install python-setuptools
#sudo easy_install pip
sudo apt-get install libzmq-dev
sudo apt-get build-dep python-zmq
sudo pip install pyzmq
python setup.py install 
sudo adduser --system --shell /bin/sh --gecos 'git version control' --group --disabled-password --home /home/git git
ssh-keygen -t rsa
sudo -H -u git gitosis-init < /tmp/id_rsa.pub
sudo chmod 755 /home/git/repositories/gitosis-admin.git/hooks/post-update

