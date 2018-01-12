# Copyright (C) 2014 SDN Hub
#
# Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3.
# You may not use this file except in compliance with this License.
# You may obtain a copy of the License at
#
#    http://www.gnu.org/licenses/gpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.

import logging
import json
import random
import ryu.utils

from ryu.lib import mac as mac_lib
from ryu.lib import ip as ip_lib
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import arp
from ryu.ofproto import ether, inet
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.app.tooyum import learning_switch
from ryu.controller import dpset

UINT32_MAX = 0xffffffff
LOG = logging.getLogger('ryu.app.tooyum.stateless_lb')
################ Main ###################

# The stateless server load balancer picks a different server for each
# request. For making the assignment, it only uses the servers it
# already knows the location of. The clients or the gateway sents along
# a request for the Virtual IP of the load-balancer. The first switch
# intercepting the request will rewrite the headers to match the actual
# server picked. So all other switches will only have to do simple
# L2 forwarding. It is possible to avoid IP header writing if alias IP
# is set on the servers. The call skip_ip_header_rewriting() will handle
# the appropriate flag setting.

class StatelessLB(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):
        super(StatelessLB, self).__init__(*args, **kwargs)
        self.rewrite_ip_header = True
        self.server_index = 0
        self.servers = []

        self.virtual_ip = None
        #self.virtual_ip = "10.0.0.5"
        self.virtual_mac = "A6:63:DD:D7:C0:C8" # Pick something dummy and

        #self.servers.append({'ip':"10.0.0.2", 'mac':"00:00:00:00:00:02"})
        #self.servers.append({'ip':"10.0.0.3", 'mac':"00:00:00:00:00:03"})
        #self.servers.append({'ip':"10.0.0.4", 'mac':"00:00:00:00:00:04"})

        #self.learning_switch = kwargs['learning_switch']
        #self.learning_switch.add_exemption({'dl_type': ether.ETH_TYPE_LLDP})
        #self.learning_switch.add_exemption({'dl_dst': self.virtual_mac})

    def set_learning_switch(self, learning_switch):
        self.learning_switch = learning_switch
        self.learning_switch.clear_exemption()
        self.learning_switch.add_exemption({'dl_dst': self.virtual_mac})

    # Users can skip doing header rewriting by setting the virtual IP 
    # as an alias IP on all the servers. This works well in single subnet
    def set_rewrite_ip_flag(self, rewrite_ip):
        if rewrite_ip == 1:
            self.rewrite_ip_header = True
        else:
            self.rewrite_ip_header = False

    def set_virtual_ip(self, virtual_ip=None):
        self.virtual_ip = virtual_ip

    def set_server_pool(self, servers=None):
        self.servers = servers

    def set_dpid(self, dpid=None):
        self.input_dpid = dpid

    def set_vport(self,vport=None):
        self.vport = vport

    def formulate_arp_reply(self, dst_mac, dst_ip):
        if self.virtual_ip == None:
            return

        src_mac = self.virtual_mac
        src_ip = self.virtual_ip
        arp_opcode = arp.ARP_REPLY
        arp_target_mac = dst_mac

        ether_proto = ether.ETH_TYPE_ARP
        hwtype = 1
        arp_proto = ether.ETH_TYPE_IP
        hlen = 6
        plen = 4

        pkt = packet.Packet()
        e = ethernet.ethernet(dst_mac, src_mac, ether_proto)
        a = arp.arp(hwtype, arp_proto, hlen, plen, arp_opcode,
                    src_mac, src_ip, arp_target_mac, dst_ip)
        pkt.add_protocol(e)
        pkt.add_protocol(a)
        pkt.serialize()

        return pkt

    def create_group_lb(self, datapath):
        buckets = []
        if self.rewrite_ip_header:
            for server in self.servers:
                LOG.error(server)
                actions = [datapath.ofproto_parser.OFPActionSetField(eth_dst=server['mac']),
                       datapath.ofproto_parser.OFPActionSetField(ipv4_dst=server['ip']),
                       datapath.ofproto_parser.OFPActionOutput(int(server['port']))]
                LOG.error(int(server['port']))
                #buckets = self.bucket_v12(datapath, action=actions)
                buckets.extend(self.bucket_v12(datapath, action=actions))
        else:
            for server in self.servers:
                actions = [datapath.ofproto_parser.OFPActionSetField(eth_dst=server.mac),
                       datapath.ofproto_parser.OFPActionOutput(server.port)]
                buckets = buckets.extend(self.bucket_v12(datapath, action=buckets))
 
        #buckets = [datapath.ofproto_parser.OFPBucket(1, 0, 0,actions)]
        self.group_v12(datapath, command=datapath.ofproto.OFPGC_DELETE, type_=datapath.ofproto.OFPGT_SELECT, groupid=100,buckets=[])
        # group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=2,type_=datapath.ofproto.OFPGT_SELECT, group_id=100)
        # datapath.send_msg(group)
        self.group_v12(datapath, command=0, type_=datapath.ofproto.OFPGT_SELECT, groupid=100, buckets=buckets)
 
 
    def bucket_v12(self, datapath, len_=0, weight=1, watch_port=0, watch_group=0,action=[]):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=action)]
        return buckets
 
    def group_v12(self, datapath, command=0, type_=0, groupid=0, buckets=None):
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_, group_id=groupid, buckets=buckets)
        datapath.send_msg(group)



    def install_lb_out2in_flow(self):
        datapath = self.dpset.get(int(self.input_dpid,16))
        LOG.error(datapath)
        self.create_group_lb(datapath=datapath)
        match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800, ipv4_dst=self.virtual_ip)
        actions = [datapath.ofproto_parser.OFPActionGroup(100)]
        inst = [datapath.ofproto_parser.OFPInstructionActions(datapath.ofproto.OFPIT_WRITE_ACTIONS, actions)]
        cookie = random.randint(0, 0xffffffffffffffff)
        mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=10,
                instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

    def install_lb_in2out_flow(self):
        datapath = self.dpset.get(int(self.input_dpid,16))
        for serverIP in self.servers :
            match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800, ipv4_src=serverIP['ip'])
            actions = [datapath.ofproto_parser.OFPActionSetField(ipv4_src=self.virtual_ip),
                       datapath.ofproto_parser.OFPActionOutput(int(self.vport)) ]
            inst = [datapath.ofproto_parser.OFPInstructionActions(datapath.ofproto.OFPIT_WRITE_ACTIONS, actions)]
            cookie = random.randint(0, 0xffffffffffffffff)
            mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=10,
                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        if self.virtual_ip == None or self.servers == None:
            return

        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether.ETH_TYPE_ARP:
            arp_hdr = pkt.get_protocols(arp.arp)[0]

            if arp_hdr.dst_ip == self.virtual_ip and arp_hdr.opcode == arp.ARP_REQUEST:

                reply_pkt = self.formulate_arp_reply(arp_hdr.src_mac,
                        arp_hdr.src_ip)

                actions = [ofp_parser.OFPActionOutput(in_port)]
                out = ofp_parser.OFPPacketOut(datapath=datapath, 
                           in_port=ofp.OFPP_ANY, data=reply_pkt.data,
                           actions=actions, buffer_id = UINT32_MAX)
                datapath.send_msg(out)

            return

        # Only handle IPv4 traffic going forward
        elif eth.ethertype != ether.ETH_TYPE_IP:
            return

        iphdr = pkt.get_protocols(ipv4.ipv4)[0]

        # Only handle traffic destined to virtual IP
        if (iphdr.dst != self.virtual_ip):
            return 

        # Only handle TCP traffic
        if iphdr.proto != inet.IPPROTO_TCP:
            return 

        tcphdr = pkt.get_protocols(tcp.tcp)[0]

        valid_servers = []
        for server in self.servers:
            outport = self.learning_switch.get_attachment_port(dpid, server['mac'])
            if outport != None:
                server['outport'] = outport
                valid_servers.append(server)

        total_servers = len(valid_servers)

        # If we there are no servers with location known, then skip
        if total_servers == 0:
            return

        # Round robin selection of servers
        index = self.server_index % total_servers
        selected_server_ip = valid_servers[index]['ip']
        selected_server_mac = valid_servers[index]['mac']
        selected_server_outport = valid_servers[index]['outport']
        self.server_index += 1
        print "Selected server", selected_server_ip

        ########### Setup route to server
        match = ofp_parser.OFPMatch(in_port=in_port,
                eth_type=eth.ethertype,  eth_src=eth.src,    eth_dst=eth.dst, 
                ip_proto=iphdr.proto,    ipv4_src=iphdr.src, ipv4_dst=iphdr.dst,
                tcp_src=tcphdr.src_port, tcp_dst=tcphdr.dst_port)

        if self.rewrite_ip_header:
            actions = [ofp_parser.OFPActionSetField(eth_dst=selected_server_mac),
                       ofp_parser.OFPActionSetField(ipv4_dst=selected_server_ip),
                       ofp_parser.OFPActionOutput(selected_server_outport) ]
        else:
            actions = [ofp_parser.OFPActionSetField(eth_dst=selected_server_mac),
                       ofp_parser.OFPActionOutput(selected_server_outport) ]

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        cookie = random.randint(0, 0xffffffffffffffff)

        mod = ofp_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=10,
                instructions=inst, buffer_id = msg.buffer_id, cookie=cookie)
        datapath.send_msg(mod)

        ########### Setup reverse route from server
        match = ofp_parser.OFPMatch(in_port=selected_server_outport,
                eth_type=eth.ethertype,  eth_src=selected_server_mac, eth_dst=eth.src, 
                ip_proto=iphdr.proto,    ipv4_src=selected_server_ip, ipv4_dst=iphdr.src,
                tcp_src=tcphdr.dst_port, tcp_dst=tcphdr.src_port)

        if self.rewrite_ip_header:
            actions = ([ofp_parser.OFPActionSetField(eth_src=self.virtual_mac),
                       ofp_parser.OFPActionSetField(ipv4_src=self.virtual_ip),
                       ofp_parser.OFPActionOutput(in_port) ])
        else:
            actions = ([ofp_parser.OFPActionSetField(eth_src=self.virtual_mac),
                       ofp_parser.OFPActionOutput(in_port) ])

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        cookie = random.randint(0, 0xffffffffffffffff)

        mod = ofp_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=10,
                instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

