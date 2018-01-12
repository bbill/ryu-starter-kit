# from controller import dpset
# s=dpset.DPset()
# a=s.get_all()
# print a
# b=s.
# from ryu.base import app_manager 
# from controller import dpset
import MySQLdb
import json
from operator import attrgetter
import logging
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.dpset import EventDP
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_3

from ryu.app.tooyum import database


LOG = logging.getLogger('ryu.monitor')

class SimpleMonitor(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self , *args, **kwargs):
		super(SimpleMonitor , self).__init__(*args, **kwargs)
		self.datapaths = {}
		self.database = database.Database()
		self.monitor_thread = hub.spawn(self._monitor)
        
	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		msg = ev.msg
		datapath = msg.datapath
		datapath.id = msg.datapath_id
    		self.datapaths[datapath.id] = datapath
		dp = hex(datapath.id)
        	if dp[-1] == 'L':
            		dp = dp[:-1]
        	self.database.add_datapath(dp)
		        
	@set_ev_cls(EventDP, MAIN_DISPATCHER)
    	def _dp_disconnect_handler(self, ev):
        	dp = ev.dp
        	if not ev.enter:
            		del self.datapaths[dp.id]
			self.database.del_datapath(hex(dp.id))
            		

	def _monitor(self):
		while True:
			if self.datapaths:
				for dp in self.datapaths.values():
					self._request_stats(dp)		
			hub.sleep(15)

	def _request_stats(self , datapath):
		self.logger.debug('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		req = parser.OFPFlowStatsRequest(datapath)
		datapath.send_msg(req)
		req = parser.OFPPortStatsRequest(datapath , 0, ofproto.OFPP_ANY)
		datapath.send_msg(req)

	@set_ev_cls(ofp_event.EventOFPFlowStatsReply , MAIN_DISPATCHER)
    	def _flow_stats_reply_handler(self , ev):
        	body = ev.msg.body
               	dp = hex(ev.msg.datapath.id)
        	if dp[-1] == 'L':
            		dp = dp[:-1]
		self.logger.info('datapath '
            	'in-port eth-dst '
            	'out-port packets bytes')
        	self.logger.info('---------------- '
            	'-------- ----------------- '
            	'-------- -------- --------')
            	#for stat in [flow for flow in body]:
            		#self.logger.info('%016x %8x %17s %8x %8d %8d',ev.msg.datapath.id,stat.match['in_port'], stat.match['eth_dst'],stat.instructions[0].actions[0].port,stat.packet_count , stat.byte_count)
		for stat in [flow for flow in body]:
			match = self.make_match(stat.match, dp)
            		self.database.add_flow(dp, str(match))
            		self.database.add_flow_sta(str(match), stat.byte_count, stat.packet_count)
			
			
				        		
	@set_ev_cls(ofp_event.EventOFPPortStatsReply , MAIN_DISPATCHER)
	def _port_stats_reply_handler(self , ev):
    		body = ev.msg.body
    		body = ev.msg.body
        	input_sta = 0
        	output_sta = 0
        	drop_sta =0 
        	for stat in sorted(body, key=attrgetter('port_no')):
            		input_sta = input_sta + stat.rx_bytes
            		output_sta = output_sta + stat.tx_bytes
            		drop_sta = drop_sta + stat.rx_errors
		
		dp = hex(ev.msg.datapath.id)
        	if dp[-1] == 'L':
            		dp = dp[:-1]
        	self.database.add_switch_sta(dp,input_sta,output_sta,drop_sta)		
		#self.logger.info('datapath port '
        	#	'rx-pkts rx-bytes rx-error '
        	#	'tx-pkts tx-bytes tx-error')
    		#self.logger.info('---------------- -------- '
        	#	'-------- -------- -------- '
        	#	'-------- -------- --------')
    		#for stat in sorted(body, key=attrgetter('port_no')):
    		#	self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
    		#		ev.msg.datapath.id, stat.port_no ,
    		#		stat.rx_packets , stat.rx_bytes , stat.rx_errors ,
    		#		stat.tx_packets , stat.tx_bytes , stat.tx_errors)


	def make_match(self, match, datapath):
        	data = {}
		data['datapath'] = datapath
		if 'udf0' in match:
			data['udf0'] = match['udf0']
		if 'udf1' in match:
			data['udf1'] = match['udf1']
		if 'udf2' in match:
			data['udf2'] = match['udf2']
		if 'udf3' in match:
			data['udf3'] = match['udf3']
        	if 'in_port' in match:
            		data['in_port'] = match['in_port']
        	if 'in_phy_port' in match:
            		data['in_phy_port'] = match['in_phy_port']
        	if 'metadata' in match:
            		data['metadata'] = match['metadata']
        	if 'eth_dst' in match:
            		data['eth_dst'] = match['eth_dst']
        	if 'eth_src' in match:
            		data['eth_src'] = match['eth_src']
        	if 'eth_type' in match:
            		data['eth_type'] = match['eth_type']
       		if 'vlan_vid' in match:
            		data['vlan_vid'] = match['vlan_vid']
        	if 'vlan_pcp' in match:
            		data['vlan_pcp'] = match['vlan_pcp']
        	if 'ip_dscp' in match:
            		data['ip_dscp'] = match['ip_dscp']
        	if 'ip_ecn' in match:
            		data['ip_ecn'] = match['ip_ecn']
        	if 'ip_proto' in match:
            		data['ip_proto'] = match['ip_proto']
        	if 'ipv4_src' in match:
            		data['ipv4_src'] = match['ipv4_src']
        	if 'ipv4_dst' in match:
            		data['ipv4_dst'] = match['ipv4_dst']
        	if 'tcp_src' in match:
            		data['tcp_src'] = match['tcp_src']
        	if 'tcp_dst' in match:
            		data['tcp_dst'] = match['tcp_dst']
        	if 'udp_src' in match:
            		data['udp_src'] = match['udp_src']
        	if 'udp_dst' in match:
            		data['udp_dst'] = match['udp_dst']
        	if 'sctp_src' in match:
            		data['sctp_src'] = match['sctp_src']
        	if 'sctp_dst' in match:
            		data['sctp_dst'] = match['sctp_dst']
        	if 'icmpv4_type' in match:
            		data['icmpv4_type'] = match['icmpv4_type']
        	if 'icmpv4_code' in match:
            		data['icmpv4_code'] = match['icmpv4_code']
        	if 'arp_op' in match:
            		data['arp_op'] = match['arp_op']
        	if 'arp_spa' in match:
            		data['arp_spa'] = match['arp_spa']
        	if 'arp_tpa' in match:
            		data['arp_tpa'] = match['arp_tpa']
        	if 'arp_sha' in match:
            		data['arp_sha'] = match['arp_sha']
        	if 'arp_tha' in match:
            		data['arp_tha'] = match['arp_tha']
        	if 'ipv6_src' in match:
            		data['ipv6_src'] = match['ipv6_src']
        	if 'ipv6_dst' in match:
            		data['ipv6_dst'] = match['ipv6_dst']
        	if 'ipv6_flabel' in match:
            		data['ipv6_flabel'] = match['ipv6_flabel']
        	if 'icmpv6_type' in match:
            		data['icmpv6_type'] = match['icmpv6_type']
        	if 'icmpv6_code' in match:
            		data['icmpv6_code'] = match['icmpv6_code']
        	if 'ipv6_nd_target' in match:
            		data['ipv6_nd_target'] = match['ipv6_nd_target']
        	if 'ipv6_nd_sll' in match:
            		data['ipv6_nd_sll'] = match['ipv6_nd_sll']
        	if 'ipv6_nd_tll' in match:
            		data['ipv6_nd_tll'] = match['ipv6_nd_tll']
        	if 'mpls_label' in match:
            		data['mpls_label'] = match['mpls_label']
        	if 'mpls_tc' in match:
            		data['mpls_tc'] = match['mpls_tc']
        	if 'mpls_bos' in match:
            		data['mpls_bos'] = match['mpls_bos']
        	if 'pbb_isid' in match:
            		data['pbb_isid'] = match['pbb_isid']
        	if 'tunnel_id' in match:
            		data['tunnel_id'] = match['tunnel_id']
        	if 'ipv6_exthdr' in match:
            		data['ipv6_exthdr'] = match['ipv6_exthdr']
        	if 'pbb_uca' in match:
            		data['pbb_uca'] = match['pbb_uca']
        	if 'tcp_flags' in match:
            		data['tcp_flags'] = match['tcp_flags']
        	if 'actset_output' in match:
            		data['actset_output'] = match['actset_output']

        	return data
