#!/bin/sh

cd ~/ryu
export PYTHONPATH=$PYTHONPATH:.


./bin/ryu-manager --observe-links --verbose ryu/app/tooyum/fileserver.py ryu/app/tooyum/host_tracker_rest.py  ryu/app/rest_topology.py ryu/app/tooyum/stateless_lb_rest.py ryu/app/tooyum/stateless_lb_rest.py ryu/app/tooyum/tap_rest.py ryu/app/ofctl_rest.py ryu/app/tooyum/run.py ryu/app/tooyum/traffic_rest.py
