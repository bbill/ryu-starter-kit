# Copyright (C) 2016 Pica8.Inc

import logging
import json
from ryu.app.tooyum import database
from webob import Response

from ryu.base import app_manager
from ryu.app.wsgi import ControllerBase, WSGIApplication,route

from ryu.ofproto import ofproto_v1_0, ofproto_v1_3

LOG = logging.getLogger('ryu.app.tooyum.traffic_rest')


class TrafficController(ControllerBase):
	def __init__(self, req, link, data, **config):
		super(TrafficController, self).__init__(req, link, data, **config)
		self.traffic_data = {}
		self.database = database.Database()

	@route('traffic', '/traffic', methods=['GET'])
	def get_all_traffic(self, req, **kwargs):
		return Response(status=200,content_type='application/json',
			body=json.dumps(self.traffic_data))
	
	@route('traffic', '/controller_info', methods=['GET'])
	def get_controller_info(self, req, **kwargs):
		info = self.database.get_controller_info()
		return Response(status=200,content_type='application/json',
			body=json.dumps(info))
	
	@route('traffic', '/dp_info', methods=['GET'])
	def get_dp_info(self, req, **kwargs):
		info = self.database.get_all_dpid()
		return Response(status=200,content_type='application/json',
			body=json.dumps(info))

	@route('traffic', '/switch_sta/{dpid}', methods=['GET'])
	def get_switch_info(self, req, dpid,**kwargs):
		info = self.database.get_switch_sta(dpid)
		return Response(status=200,content_type='application/json',
			body=json.dumps(info))
	
	@route('traffic', '/flow_type/{dpid}', methods=['GET'])
  	def get_flow(self, req, dpid,**kwargs):
    		info = self.database.get_match_by_dpid(dpid)
    		return Response(status=200,content_type='application/json',
      			body=json.dumps(info))

	@route('traffic', '/flow_sta/{match}', methods=['GET'])
  	def get_flow_sta(self, req, match,**kwargs):
    		info = self.database.get_flow_sta_by_match(match)
    		return Response(status=200,content_type='application/json',
      			body=json.dumps(info))

	@route('traffic', '/overview', methods=['GET'])
  	def get_overview(self, req, **kwargs):
    		info = self.database.get_overview()
    		return Response(status=200,content_type='application/json',
      			body=json.dumps(info))

class TrafficRestApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION,
                    ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'wsgi': WSGIApplication,
    }

    def __init__(self, *args, **kwargs):
        super(TrafficRestApi, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        # traffic_data = kwargs['traffic_data']
        self.waiters = {}
        self.data = {}
        # self.data['traffic_data'] = traffic_data
        self.data['waiters'] = {}
     

        wsgi.registory['TrafficController'] = self.data
        mapper = wsgi.mapper

        mapper.connect('traffic', '/traffic',
                       controller=TrafficController, action='get_all_traffic',
                       conditions=dict(method=['GET']))

	mapper.connect('traffic', '/controller_info',
                       controller=TrafficController, action='get_controller_info',
                       conditions=dict(method=['GET']))

	mapper.connect('traffic', '/dp_info',
                       controller=TrafficController, action='get_dp_info',
                       conditions=dict(method=['GET']))

	mapper.connect('traffic', '/switch_sta/{dpid}', 
        		controller=TrafficController, action='get_switch_info',
               		conditions=dict(method=['GET']))

	mapper.connect('traffic', '/flow_type/{dpid}', 
                 controller=TrafficController, action='get_flow',
                     conditions=dict(method=['GET']))

	mapper.connect('traffic', '/flow_sta/{match}', 
                 controller=TrafficController, action='get_flow_sta',
                     conditions=dict(method=['GET']))

	mapper.connect('traffic', '/overview', 
                 controller=TrafficController, action='get_overview',
                     conditions=dict(method=['GET']))
