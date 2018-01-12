import MySQLdb
import time
import datetime
import logging

LOG = logging.getLogger('ryu.app.tooyum.database')

class Database :
	
	def __init__(self ):
		self.conn= MySQLdb.connect(
	        host='localhost',
	        port = 3306,
	        user='root',
	        passwd='pica8',
	        db ='test',
	        )
		# self.cur = conn.cursor()
	
	def get_overview(self):
		overview_info = {}
		overview_info['dp']=[]
		overview_info['input'] = []
		overview_info['output'] = []
		overview_info['drop'] = []
		overview_info['flow_count'] = []
		flow_count = []
		cur = self.conn.cursor()
		# sqli =cur.execute("select sw_sta_dpid,sw_sta_input,sw_sta_output,sw_sta_drop,max(sw_sta_time) from switch_statistics group by sw_sta_dpid order by sw_sta_input+sw_sta_output limit 5")
		sqli =cur.execute("select sw_sta_dpid,max(sw_sta_time) from switch_statistics group by sw_sta_dpid");
		info = cur.fetchmany(sqli)
		for i in info:
			sqli =cur.execute("select sw_sta_dpid,sw_sta_input,sw_sta_output,sw_sta_drop from switch_statistics where sw_sta_dpid='"+i[0]+"' and sw_sta_time='"+i[1].strftime('%Y-%m-%d %H:%M:%S')+"'")
			flow_info =cur.fetchone()
			overview_info['dp'].append(flow_info[0])
			overview_info['input'].append(flow_info[1])
			overview_info['output'].append(flow_info[2])
			overview_info['drop'].append(flow_info[3])

			# overview_info['dp'].append(i[0])
			# overview_info['input'].append(i[1])
			# overview_info['output'].append(i[2])
			# overview_info['drop'].append(i[3])

			sqli = cur.execute("select count(*) from flow where dpid='"+i[0]+"'")
			overview_info['flow_count'].append(cur.fetchone()[0])

		cur.close()
		self.conn.commit()
		return overview_info

	def get_controller_info(self):
		info = {}

		cpu_load = open('/proc/stat', 'r').readline()
    		user, nice, system, idle = tuple(map(lambda x: int(x), cpu_load.split()[1:5]))
    		info_cpu_load = 100.0 * (user + nice + system)/(user + nice + system + idle)
    		info['cpu_load'] = int(info_cpu_load*100)

    		mem_load = open('/proc/meminfo', 'r').readlines()
    		mem_total = float(mem_load[0].split()[1])
    		mem_free = float(mem_load[1].split()[1])
    		info_cpu_load = 100.0 * (1-mem_free/mem_total)
    		info['mem_load'] = int(info_cpu_load)

		import os
    		hd={}
    		disk = os.statvfs('/')
    		hd['available'] = float(disk.f_bsize * disk.f_bavail)
    		hd['capacity'] = float(disk.f_bsize * disk.f_blocks)
    		hd['used'] = float((disk.f_blocks - disk.f_bfree) * disk.f_frsize)
    		res = {}
    		res['used'] = round(hd['used'] / (1024 * 1024 * 1024), 2)
    		res['capacity'] = round(hd['capacity'] / (1024 * 1024 * 1024), 2)
    		res['available'] = res['capacity'] - res['used']
    		info['disk_load'] = int(round(float(res['used']) / res['capacity'] * 100))

		return info

	def add_datapath(self, datapath):
		cur = self.conn.cursor()
		sqli="insert ignore into switch values('"+datapath+"')"
		cur.execute(sqli)
		cur.close()
		self.conn.commit()
	
	def del_datapath(self, datapath):
		cur = self.conn.cursor()
		sqli="delete from switch where dpid='"+datapath+"'"
		cur.execute(sqli)
		cur.close()
		self.conn.commit()
	
	def add_flow(self, dpid, match):
		cur = self.conn.cursor()
		sqli='insert ignore into flow (dpid, flow_match) values(%s, %s)'
		cur.execute(sqli,(dpid, match))
		cur.close()
		self.conn.commit()

	def add_flow_sta(self, match, byte, packets):
		cur = self.conn.cursor()
		cur.execute('select flow_id from flow where flow_match="'+match+'"')
		flow_id = cur.fetchone()[0]

		sqli="insert into flow_statistics (flow_sta_flow_id, flow_sta_byte, flow_sta_packets) values(%s,%s,%s)"
		cur.execute(sqli,(flow_id, byte, packets))
		
		
		cur.close()
		self.conn.commit()

		return flow_id
	
	def add_switch_sta(self, datapath, input_sta, output_sta, drop_sta):
		cur = self.conn.cursor()
		sqli="insert into switch_statistics (sw_sta_input, sw_sta_output, sw_sta_drop, sw_sta_dpid) values(%s,%s,%s,%s)"
		cur.execute(sqli,(input_sta, output_sta, drop_sta, datapath))
		cur.close()
		self.conn.commit()

	def get_all_dpid(self):
		dp = []
		cur = self.conn.cursor()
		sqli =cur.execute("select * from switch")
		info = cur.fetchmany(sqli)
		for i in info:
			dp.append(i[0])
		
		cur.close()
		self.conn.commit()
		
		return dp
	
	def get_match_by_dpid(self, dpid):
		flows = []
		cur = self.conn.cursor()
		sqli =cur.execute('select * from flow where dpid="'+dpid+'"')
		info = cur.fetchmany(sqli)
		for i in info:
			flows.append(i[2])
		cur.close()
		self.conn.commit()

		return flows

	def get_flow_sta_by_match(self, match):
		flow_sta = {}
		flow_sta['byte'] = []
		flow_sta['packet'] = []
		cur = self.conn.cursor()
		cur.execute('select * from flow where flow_match="'+match+'"')
		flow_id = str(cur.fetchone()[0])

		sqli =cur.execute('select * from flow_statistics where flow_sta_flow_id="'+flow_id+'" order by flow_sta_time desc limit 240')
		info = cur.fetchmany(sqli)

		for index in range(len(info)):
			if index>0 :
				temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
				byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
				packet_data = (float(info[index-1][3])-float(info[index][3]))/15
				flow_sta['byte'].append([temp_time, byte_data])
				flow_sta['packet'].append([temp_time, packet_data])

		# for i in info:
		# 	temp_time = time.mktime((i[1]+datetime.timedelta(hours=8)).timetuple())*1000
		# 	flow_sta['byte'].append([temp_time, i[2]])
		# 	flow_sta['packet'].append([temp_time, i[3]])
		cur.close()
		self.conn.commit()

		return flow_sta

	def get_switch_sta(self, datapath):
		sta_info = {}
		sta_info['input'] = []
		sta_info['output'] = []
		sta_info['drop'] = []
		cur = self.conn.cursor()
		sqli =cur.execute("select * from switch_statistics where sw_sta_dpid='"+datapath+"'")
		info = cur.fetchmany(sqli)
		for i in info:
    			temp_time = time.mktime((i[1]+datetime.timedelta(hours=8)).timetuple())*1000
    			sta_info['input'].append([temp_time,i[2]])
    			sta_info['output'].append([temp_time,i[3]])
    			sta_info['drop'].append([temp_time,i[4]])
		cur.close()
		self.conn.commit()

		return sta_info
	def get_security_sta(self, datapath):
		sta_security = {}
		sta_security['tcp']=[]
		sta_security['dns']=[]
		sta_security['http']=[]
		sta_security['icmp']=[]
		sta_security['ntp']=[]
		sta_security['udp_tcp']=[]

		cur = self.conn.cursor()
		#### TCP FLOW
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf0\': (393216, 16711680), \'udf2\': (131072, 268369920), \'datapath\': \''+datapath+'\'}"')
		temp_cur = cur.fetchone()
		if	temp_cur != None:
			flow_id = str(temp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+flow_id+' order by flow_sta_time desc limit 240')
			info = cur.fetchmany(sqli)

			for index in range(len(info)):
				if index>0 :
					temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
					byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
					sta_security['tcp'].append([temp_time, byte_data])

		#### DNS
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf1\': (53, 65535), \'udf0\': (1114112, 16711680), \'datapath\': \''+datapath+'\'}"')
		temp_cur = cur.fetchone()
		if	temp_cur != None:
			flow_id = str(temp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+flow_id+' order by flow_sta_time desc limit 240')
			info = cur.fetchmany(sqli)

			for index in range(len(info)):
				if index>0 :
					temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
					byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
					sta_security['dns'].append([temp_time, byte_data])

		
		#### HTTP
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf1\': (80, 65535), \'udf0\': (393216, 16711680), \'udf3\': (1195725824, 4294967040), \'datapath\': \''+datapath+'\'}"')
		temp_cur = cur.fetchone()
		if	temp_cur != None:
			flow_id = str(temp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+flow_id+' order by flow_sta_time desc limit 240')
			info = cur.fetchmany(sqli)

			for index in range(len(info)):
				if index>0 :
					temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
					byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
					sta_security['http'].append([temp_time, byte_data])

		#### ICMP
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf0\': (65536, 16711680), \'datapath\': \''+datapath+'\'}"')
	        temp_cur = cur.fetchone()
		if	temp_cur != None:
			flow_id = str(temp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+flow_id+' order by flow_sta_time desc limit 240')
			info = cur.fetchmany(sqli)

			for index in range(len(info)):
				if index>0 :
					temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
					byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
					sta_security['icmp'].append([temp_time, byte_data])

		#### NTP 
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf1\': (24699, 65535), \'udf0\': (1114112, 16711680), \'datapath\': \''+datapath+'\'}"')
		temp_cur = cur.fetchone()
		if	temp_cur != None:
			flow_id = str(temp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+flow_id+' order by flow_sta_time desc limit 240')
			info = cur.fetchmany(sqli)

			for index in range(len(info)):
				if index>0 :
					temp_time = time.mktime((info[index][1]+datetime.timedelta(hours=8)).timetuple())*1000
					byte_data = (float(info[index-1][2])-float(info[index][2]))/15*8
					sta_security['ntp'].append([temp_time, byte_data])
		
		#### UDP/TCP
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf0\': (1114112, 16711680), \'datapath\': \''+datapath+'\'}"')
		udp_cur = cur.fetchone()
		sqli = cur.execute('select flow_id from flow where flow_match="{\'udf0\': (393216, 16711680), \'datapath\': \''+datapath+'\'}"')
		tcp_cur = cur.fetchone()
		if	udp_cur != None and tcp_cur != None:
			udp_id = str(udp_cur[0])
			tcp_id = str(tcp_cur[0])
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+udp_id+' order by flow_sta_time desc limit 240')
			udp_info = cur.fetchmany(sqli)
			sqli = cur.execute('select * from flow_statistics where flow_sta_flow_id='+tcp_id+' order by flow_sta_time desc limit 240')
			tcp_info = cur.fetchmany(sqli)

			i = 1
			while i<min(len(udp_info),len(tcp_info)):
				temp_time = time.mktime((udp_info[i][1]+datetime.timedelta(hours=8)).timetuple())*1000
				temp_udp = (float(udp_info[i-1][2])-float(udp_info[i][2]))/15.0
				temp_tcp = (float(tcp_info[i-1][2])-float(tcp_info[i][2]))/15.0
				if temp_udp == 0 and temp_tcp == 0:
					temp_udp = 1
					temp_tcp = 1
				sta_security['udp_tcp'].append([temp_time, temp_udp/(temp_udp+temp_tcp)])
				i=i+1
				


		### cur close
		cur.close()
		self.conn.commit()

		return sta_security
