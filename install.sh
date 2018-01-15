#!/bin/bash
cd
[ -d ~/ryu/ryu/app ] || echo "Please install RYU first!"
git clone https://github.com/bbill/ryu-starter-kit.git ~/ryu/ryu/app/tooyum
sudo apt-get install -y mysql-server libmysqld-dev
sudo pip install networkx MySQL-python

