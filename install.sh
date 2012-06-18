#!/bin/sh
#sudo apt-get install python-setuptools
#sudo easy_install pip
#sudo apt-get install git

#sudo apt-get install libzmq-dev
#sudo apt-get build-dep python-zmq
#sudo pip install pyzmq

#cd /home
#sudo adduser --system --shell /bin/sh --gecos 'git version control' --group --disabled-password --home /home/git git
#sudo mkdir /home/git/.ssh
#sudo ssh-keygen -t rsa #create file in /home/git/.ssh/id_rsa

sudo git clone git://github.com/jvillama/gitosis.git
cd gitosis

sudo python setup.py install
sudo chown -R git:git /home/git/.ssh
sudo gitosis-init < /home/git/.ssh/id_rsa.pub
#sudo -H -u git gitosis-init < /home/git/.ssh/id_rsa.pub
sudo chmod 755 /home/git/repositories/gitosis-admin.git/hooks/post-update

#sudo vi /etc/gitosis/config
sudo mkdir /etc/gitosis
sudo cp config /etc/gitosis/config

#sudo nosetests gitosis/test/test_dcontrol.py
