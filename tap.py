# Copyright (C) 2014 SDN Hub
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import struct
import random
import ryu.utils

from ryu.base import app_manager
from ryu.topology import event as topo_event
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import HANDSHAKE_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4

from ryu.ofproto import ether
from ryu.controller import dpset

import networkx as nx

LOG = logging.getLogger('ryu.app.tooyum.tap')

class StarterTap(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(StarterTap, self).__init__(*args, **kwargs)

        self.broadened_field = {'dl_host': ['dl_src', 'dl_dst'],
                                'nw_host': ['nw_src', 'nw_dst'],
                                'tp_port': ['tp_src', 'tp_dst']}


    @set_ev_cls(ofp_event.EventOFPErrorMsg, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
      
        LOG.info('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s',
                        msg.type, msg.code, ryu.utils.hex_array(msg.data))


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        # Delete all existing rules on the switch
        mod = ofproto_parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,
                             out_port=ofproto.OFPP_ANY,out_group=ofproto.OFPG_ANY)
        datapath.send_msg(mod)


    def change_field(self, old_attrs, original, new):
        new_attrs = {}
        for key, val in old_attrs.items():
            if (key == original):
                new_attrs[new] = val
            else:
                new_attrs[key] = val
        return new_attrs

    def start_security(self, dpid):
        datapath = self.dpset.get(int(dpid,16))
        
        if datapath is None:
            LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
            return False

        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ######## Cookie might come handy
        cookie = 0x333333333333333
        ######## init inst
        actions = [ofproto_parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0)]
        inst = [ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        ######## Create tcp syc udf match & send flow
        tcp_match = {}
        tcp_match['udf0']='0x60000/0xff0000'
        tcp_match['udf2']='0x20000/0xfff0000'
        
        match = ofctl_v1_3.to_match(datapath, tcp_match)
        
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)

        datapath.send_msg(mod)
        ######## Create dns query udf match & send flow
        dns_match ={}
        dns_match['udf0']='0x110000/0xff0000'
        dns_match['udf1']='0x00000035/0x0000ffff'

        match = ofctl_v1_3.to_match(datapath, dns_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

        ######## Create http udf match & send flow
        http_match ={}
        http_match['udf0']='0x60000/0xff0000'
        http_match['udf1']='0x00000050/0x0000ffff'
        http_match['udf3']='0x47455400/0xffffff00'

        match = ofctl_v1_3.to_match(datapath, http_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

        ######## Create icmp udf match & send flow
        icmp_match={}
        icmp_match['udf0']='0x10000/0xff0000'
        match = ofctl_v1_3.to_match(datapath, icmp_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

        ######## Create ntp attack udf match & send flow
        ntp_match={}
        ntp_match['udf0']='0x110000/0xff0000'
        ntp_match['udf1']='0x0000607B/0x0000ffff'
        match = ofctl_v1_3.to_match(datapath, ntp_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

        ######## Create udp/tcp udf match & send flow (2 flows)
        udp_tcp_match={}
        udp_tcp_match['udf0']='0x110000/0xff0000'
        match = ofctl_v1_3.to_match(datapath, udp_tcp_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,priority=1000,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

        udp_tcp_match={}
        udp_tcp_match['udf0']='0x60000/0xff0000'
        match = ofctl_v1_3.to_match(datapath, udp_tcp_match)
        mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,priority=1000,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
        datapath.send_msg(mod)

    def stop_security(self, dpid):
        datapath = self.dpset.get(int(dpid,16))
        
        if datapath is None:
            LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
            return False

        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ######## Cookie might come handy
        cookie = 0x333333333333333
	cookie_mask = 0xffffffffffffffff 

        mod = ofproto_parser.OFPFlowMod(datapath=datapath, table_id=250, command=ofproto.OFPFC_DELETE,
                              out_port=ofproto.OFPP_ANY,out_group=ofproto.OFPG_ANY,cookie=cookie,cookie_mask=cookie_mask)

        datapath.send_msg(mod)

    def handle_security(self, dpid, mode,operation):
        datapath = self.dpset.get(int(dpid,16))
        
        if datapath is None:
            LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
            return False

        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ##### create meter
        mode_id = {'tcp':250,'http':251,'icmp':252,'dns':253,'ntp':254,'udp_tcp':255}
        
        meter_id = mode_id[mode]
	LOG.error(meter_id)
        meter_rate = 1000

        mod = ofproto_parser.OFPMeterMod(
                    datapath=datapath, command=ofproto.OFPMC_DELETE, flags=10,
                    meter_id=meter_id)

        datapath.send_msg(mod)

        band = ofproto_parser.OFPMeterBandDrop(rate=meter_rate, burst_size=1000, type_=1, len_=16)

        bands = [band]

        mod = ofproto_parser.OFPMeterMod(
                    datapath=datapath, command=ofproto.OFPMC_ADD, flags=5,
                    meter_id=meter_id,bands=bands)
	datapath.send_msg(mod)

        #### send flow
        ######## Cookie might come handy
        cookie = 0x333333333333333
        ######## init inst
	if operation == 'protect':
        	actions = [ofproto_parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0)]
        	inst = [ofproto_parser.OFPInstructionMeter(meter_id=meter_id),ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
	if operation == 'clear':
        	actions = [ofproto_parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0)]
        	inst = [ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        ######## Create tcp syc udf match & send flow
        if mode == 'tcp':    
            tcp_match = {}
            tcp_match['udf0']='0x60000/0xff0000'
            tcp_match['udf2']='0x20000/0xfff0000'
            
            match = ofctl_v1_3.to_match(datapath, tcp_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)

            datapath.send_msg(mod)
        ######## Create dns query udf match & send flow
        if mode == 'dns':   
            dns_match ={}
            dns_match['udf0']='0x110000/0xff0000'
            dns_match['udf1']='0x00000035/0x0000ffff'

            match = ofctl_v1_3.to_match(datapath, dns_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)

        ######## Create http udf match & send flow
        if mode == 'http':    
            http_match ={}
            http_match['udf0']='0x60000/0xff0000'
            http_match['udf1']='0x00000050/0x0000ffff'
            http_match['udf3']='0x47455400/0xffffff00'

            match = ofctl_v1_3.to_match(datapath, http_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)

        ######## Create icmp udf match & send flow
        if mode == 'icmp':    
            icmp_match={}
            icmp_match['udf0']='0x10000/0xff0000'
            match = ofctl_v1_3.to_match(datapath, icmp_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)

        ######## Create ntp attack udf match & send flow
        if mode == 'ntp':    
            ntp_match={}
            ntp_match['udf0']='0x110000/0xff0000'
            ntp_match['udf1']='0x0000607B/0x0000ffff'
            match = ofctl_v1_3.to_match(datapath, ntp_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)

        ######## Create udp/tcp udf match & send flow (2 flows)
        if mode == 'udp/tcp':
            udp_tcp_match={}
            udp_tcp_match['udf0']='0x110000/0xff0000'
            match = ofctl_v1_3.to_match(datapath, udp_tcp_match)
            mod = ofproto_parser.OFPFlowMod(
                                datapath=datapath, match=match, table_id=250,priority=1000,
                                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                                instructions=inst, cookie=cookie)
            datapath.send_msg(mod)


    def create_firewall(self, filter_data):
        LOG.debug("Creating tap with filter = %s", str(filter_data))

        dpid = filter_data['dpid']
        if 'priority' in filter_data:
            priority = filter_data['priority']
        else:
            priority = 32768

        datapath = self.dpset.get(int(dpid,16))
        if datapath is None:
            LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
            return False
        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ######## Create match
        match = ofctl_v1_3.to_match(datapath, filter_data['fields'])

        ######## Cookie might come handy
        cookie = 0x2222222222222222

        ######## init inst
        actions = []
        inst = []


        if 'normal' in filter_data['actions']:
            actions.append(ofproto_parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0))

        if 'drop' in filter_data['actions']:
            actions = []

        inst.append(ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions))


        mod = ofproto_parser.OFPFlowMod(
                datapath=datapath, match=match, priority=priority,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                instructions=inst, cookie=cookie)

        datapath.send_msg(mod)

    def clear_firewall(self, dpid):
        datapath = self.dpset.get(int(dpid,16))
        
        if datapath is None:
            LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
            return False

        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ######## Cookie might come handy
        cookie = 0x2222222222222222
	cookie_mask = 0xffffffffffffffff 

        mod = ofproto_parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,
                              out_port=ofproto.OFPP_ANY,out_group=ofproto.OFPG_ANY,cookie=cookie,cookie_mask=cookie_mask)

        datapath.send_msg(mod)




    def create_tap(self, filter_data):
        LOG.debug("Creating tap with filter = %s", str(filter_data))

        # If dl_host, nw_host or tp_port are used, the recursively call the individual filters.
        # This causes the match to expand and more rules to be programmed.
        result = True
        filter_data.setdefault('fields', {})
        filter_fields = filter_data['fields']

        for key, val in self.broadened_field.iteritems():
            if key in filter_fields:
                for new_val in val:
                    filter_data['fields'] = self.change_field(filter_fields, key, new_val)
                    result = result and self.create_tap(filter_data)

                return result

        # If match fields are exact, then proceed programming switches

        # Iterate over all the sources and sinks, and collect the individual
        # hop information. It is possible that a switch is both a source,
        # a sink and an intermediate hop.
        for source in filter_data['sources']:
            for sink in filter_data['sinks']:

                # Handle error case
                if source == sink:
                    continue

                # In basic version, source and sink are same switch
                if source['dpid'] != sink['dpid']:
                    LOG.debug("Mismatching source and sink switch")
                    return False
                # ychen modify
                datapath = self.dpset.get(int(source['dpid'],16))
                

                # If dpid is invalid, return
                if datapath is None:
                    LOG.debug("Unable to get datapath for id = %s", str(source['dpid']))
                    return False

                ofproto = datapath.ofproto
                ofproto_parser = datapath.ofproto_parser

                in_port = source['port_no']
                out_port = sink['port_no']
                filter_fields = filter_data['fields'].copy()

                ######## Create action list
                if out_port == 'Normal':
                    actions = [ofproto_parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0)]
                else:
                    actions = [ofproto_parser.OFPActionOutput(out_port)]

                ######## Create match
                if in_port != 'all':  # If not sniffing on all in_ports
                    filter_fields['in_port'] = in_port
                
                match = ofctl_v1_3.to_match(datapath, filter_fields)

                		

                ######## Cookie might come handy
                #cookie = random.randint(0, 0xffffffffffffffff)
                cookie = 0x1111111111111111

                ######## init inst
                inst = [] 
                ######## meter add
                if filter_data['qos']:
                    
                    meter_id = int(filter_data['qos']['meter_id'])
                    meter_rate = int(filter_data['qos']['meter_rate'])

                    mod = ofproto_parser.OFPMeterMod(
                                datapath=datapath, command=ofproto.OFPMC_DELETE, flags=10,
                                meter_id=meter_id)

                    datapath.send_msg(mod)

                    band = ofproto_parser.OFPMeterBandDrop(rate=meter_rate, burst_size=1000, type_=1, len_=16)

                    bands = [band]

                    mod = ofproto_parser.OFPMeterMod(
                                datapath=datapath, command=ofproto.OFPMC_ADD, flags=5,
                                meter_id=meter_id,bands=bands)

                    datapath.send_msg(mod)

                    inst.append(ofproto_parser.OFPInstructionMeter(meter_id=meter_id))
                
                
                inst.append(ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions))

                # install the flow in the switch
                if 'udf0' in filter_data['fields']:
                    mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, table_id=250,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
                else:
                    mod = ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, 
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            instructions=inst, cookie=cookie)
                LOG.info("the content of filter is %s ", mod)

                datapath.send_msg(mod)

                LOG.debug("Flow inserted to switch %x: cookie=%s, out_port=%d, match=%s",
                                  datapath.id, str(cookie), out_port, str(filter_fields))

        LOG.info("Created tap with filter = %s", str(filter_data))
        return True


    def delete_tap(self, data):
        datapath = self.dpset.get(int(data['dpid'],16))

        # If dpid is invalid, return
        if datapath is None:
            return
        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser

        ######## Cookie might come handy
        # cookie = random.randint(0, 0xffffffffffffffff)
        cookie = 0x1111111111111111
	cookie_mask = 0xffffffffffffffff
                
        mod = ofproto_parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,
                          out_port=ofproto.OFPP_ANY,out_group=ofproto.OFPG_ANY,cookie=cookie,cookie_mask=cookie_mask)

        datapath.send_msg(mod)

        mod = ofproto_parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,table_id=250,
                          out_port=ofproto.OFPP_ANY,out_group=ofproto.OFPG_ANY,cookie=cookie,cookie_mask=cookie_mask)

        datapath.send_msg(mod)

        
