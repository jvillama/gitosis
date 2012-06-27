#!/bin/sh

# Assuming the following have been executed:
#sudo apt-get install python-setuptools
#sudo easy_install pip
#sudo apt-get install git

#sudo apt-get install libzmq-dev
#sudo apt-get build-dep python-zmq
#sudo pip install pyzmq

#cd /home/git
#sudo git clone git://github.com/jvillama/gitosis.git
#cd gitosis

if [ $# -eq 1 ]
then
    sudo python setup.py install
    sudo adduser --system --shell /bin/sh --gecos 'git version control' --group --disabled-password --home /home/git git
    #sudo mkdir /home/git/.ssh
    #sudo chown -R git:git /home/git/.ssh
    #sudo ssh-keygen -t rsa #create file in /home/git/.ssh/id_rsa
    sudo cp $1 /tmp/tmp.pub
    sudo chown git:git /tmp/tmp.pub
    sudo -H -u git gitosis-init < /tmp/tmp.pub #/home/git/.ssh/id_rsa.pub
    sudo chmod 755 /home/git/repositories/gitosis-admin.git/hooks/post-update
    sudo mkdir /etc/gitosis
    sudo cp config /etc/gitosis/config
else
    echo Please provide one pub key argument
fi

# To test:
#sudo nosetests gitosis/test/test_dcontrol.py
