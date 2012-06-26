#!/bin/sh

#sudo apt-get install python-setuptools
#sudo easy_install pip
#sudo apt-get install git

#sudo apt-get install libzmq-dev
#sudo apt-get build-dep python-zmq
#sudo pip install pyzmq

#sudo adduser --system --shell /bin/sh --gecos 'git version control' --group --disabled-password --home /home/git git
#sudo mkdir /home/git/.ssh
#sudo chown -R git:git /home/git/.ssh
#sudo ssh-keygen -t rsa #create file in /home/git/.ssh/id_rsa

#cd /home/git
#sudo git clone git://github.com/jvillama/gitosis.git
#sudo mkdir /etc/gitosis
#sudo cp config /etc/gitosis/config

#cd gitosis

#sudo chown -R git:git /home/git
if [ $# -eq 1 ]; then
    sudo python setup.py install
    sudo -H -u git gitosis-init < $1 #/home/git/.ssh/id_rsa.pub
    sudo chmod 755 /home/git/repositories/gitosis-admin.git/hooks/post-update
else
    echo Please provide one pub key argument
fi

# To test:
#sudo nosetests gitosis/test/test_dcontrol.py
