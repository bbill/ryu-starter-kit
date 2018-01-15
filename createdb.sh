#!/bin/bash
mysql -uroot -ppswdtooyum <<MYSQL_SCRIPT
CREATE DATABASE test;
use test;
create table flow(
	flow_id int auto_increment PRIMARY KEY,
	dpid varchar(50) NOT NULL,
	flow_match varchar(500) NOT NULL UNIQUE
);
create table flow_statistics(
	flow_sta_id int auto_increment PRIMARY KEY,
	flow_sta_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	flow_sta_byte varchar(20) NOT NULL,
	flow_sta_packets varchar(20) NOT NULL,
	flow_sta_flow_id int NOT NULL,
	foreign key(flow_sta_flow_id) references flow(flow_id)  ON UPDATE CASCADE ON DELETE CASCADE	
);
create table switch(
	dpid varchar(50) PRIMARY KEY
);
create table switch_statistics(
	sw_sta_id int auto_increment PRIMARY KEY,
	sw_sta_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	sw_sta_input double NOT NULL,
	sw_sta_output double NOT NULL,
	sw_sta_drop double NOT NULL,
	sw_sta_dpid varchar(50) NOT NULL,
	foreign key(sw_sta_dpid) references switch(dpid)  ON UPDATE CASCADE ON DELETE CASCADE
);
MYSQL_SCRIPT
