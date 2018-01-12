/*
 * Copyright (C) 2014 SDN Hub
 *
 * Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3.
 * You may not use this file except in compliance with this License.
 * You may obtain a copy of the License at
 *
 *    http://www.gnu.org/licenses/gpl-3.0.txt
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied.
 */

var url = "http://" + location.hostname + ":8080";
var originalMain;

var portMap = {};

var line_height = $("#input-table").outerHeight(true)+12;
var flow_select_height = $("#flow-select").outerHeight(true);
var chart_height = line_height-flow_select_height-30;
$('#chart-part').css('height',line_height+'px');

// FireWall SET:
// $('#layer4_well').height($('#layer3_well').height());

function updateSwitchList() {
    var switchSelect = document.getElementById("switch");
    $.getJSON(url.concat("/v1.0/topology/switches"), function(switches){
        $.each(switches, function(index, value){
            var el = document.createElement("option");
            el.textContent = value.dpid;
            el.value = value.dpid;
            switchSelect.appendChild(el);

            portMap[value.dpid] = value.ports;
        });
    }).then(updatePorts);
}

function updatePorts() {
    var srcPortSelect = document.getElementById("src-ports");
    removeAllChildren(srcPortSelect);

    var allEl = document.createElement("option");
    allEl.textContent = "all";
    allEl.value = "all";
    allEl.setAttribute('selected', 'selected');
    srcPortSelect.appendChild(allEl);

    var sinkPortSelect = document.getElementById("sink-ports");
    removeAllChildren(sinkPortSelect);

    var normal = document.createElement("option");
    normal.textContent = 'Normal';
    sinkPortSelect.appendChild(normal);
    
    var dpid = $('#switch').val();
    $.each(portMap[dpid], function(key, value) {
        var portNum = parseInt('0x'+value.port_no);
        var el = document.createElement("option");
        el.textContent = portNum;
        el.value = portNum;
        srcPortSelect.appendChild(el);

        el = document.createElement("option");
        el.textContent = portNum;
        el.value = portNum;
        sinkPortSelect.appendChild(el);
   });
}

/* Format of the POST data is as follows:

{'fields': {'  'dl_src': mac string,
               'dl_dst': mac string,
               'dl_type': int,
               'dl_vlan': int,
               'nw_src': ip string,
               'nw_dst': ip string,
               'nw_proto': int,
               'tp_src': int,
               'tp_dst': int},
'sources': list of {'dpid': int, 'port_no': int},
'sinks': list of {'dpid': int, 'port_no': int}
}

 */

function makePostData() {
    var tapInfo = {};
    var dpid = $('#switch').val();
    var srcPorts = $('#src-ports').val();
    var sinkPorts = $('#sink-ports').val();
    var qos_id = $('#meter_id').val();
    var qos_rate = $('#meter_rate').val();

    // var vni = parseInt($('#vni').val());

    var udf_0 = $('#udf-0').val();
    var udf_1 = $('#udf-1').val();
    var udf_2 = $('#udf-2').val();
    var udf_3 = $('#udf-3').val();



    // var tp_src = $('#tp_src').val();
    // var

    // if (sinkPorts == undefined) {
    //     alert("Sink ports need to be specified.");
    //     return undefined;
    // } 


    tapInfo['sources'] = [];
    tapInfo['sinks'] = [];
    tapInfo['fields'] = {};
    tapInfo['qos'] = {};
    // tapInfo['udf'] = {}

    
    // if(vni != undefined && vni !="" && !isNaN(vni)){
    //     tapInfo['udf']['vni'] = vni;   
    // }

    if(qos_id && qos_rate){
        tapInfo['qos']['meter_id'] = qos_id;
        tapInfo['qos']['meter_rate'] = qos_rate;
    }
    if ($.inArray('all', srcPorts) != -1)
         //tapInfo.sources.push({'dpid': parseInt(dpid), 'port_no': 'all'});
         tapInfo.sources.push({'dpid': dpid, 'port_no': 'all'});
    else {
        $.each(srcPorts, function(index, value) {
            //port = {'dpid': parseInt(dpid), 'port_no': parseInt(value)};
            port = {'dpid': dpid, 'port_no': parseInt(value)};
            tapInfo.sources.push(port);
            //alert(dpid);
            //alert(parseInt(value));
        });
    }
    $.each(sinkPorts, function(index, value) {
        //var port = {'dpid': parseInt(dpid), 'port_no': parseInt(value)};
        var port = {'dpid': dpid, 'port_no': parseInt(value)};
        if(value == 'Normal'){
            port['port_no']='Normal';
        }
        tapInfo.sinks.push(port);
    });

    var l4portClass = $('#l4-class').val();
    var l4portStr = parseInt($('#l4-port').val());
    var macStr = $('#mac-addr').val();
    var ipStr = $('#ip-addr').val();
    var trafficType = $('#traffic-type').val();
    var macClass = $('#mac-class').val();
    var ipClass = $('#ip-class').val();

    
    if (l4portClass != "--Ignore--") {
        if( l4portStr == undefined || l4portStr ==""){
            alert("L4-port needs to be specified.");
            return undefined;
        }
    }
    if (l4portClass == 'tp_src'){
        tapInfo.fields['tp_src'] = l4portStr;
    }
    else if(l4portClass == 'tp_dst'){
        tapInfo.fields['tp_dst'] = l4portStr;
    }


    if (macClass != "--Ignore--") {
        if (macStr == undefined || macStr=="") {
            alert("MAC address needs to be specified.");
            return undefined;
        }
    }
    if (macClass == 'Source') 
        tapInfo.fields['dl_src'] = macStr;
    else if (macClass == 'Destination') 
        tapInfo.fields['dl_dst'] = macStr;
    else if (macClass == 'Src or Dest') 
        tapInfo.fields['dl_host'] = macStr;

    

    if (ipClass != "--Ignore--") {
        if (ipStr == undefined || ipStr=="") {
            alert("MAC address needs to be specified.");
            return undefined;
        }
        tapInfo.fields['dl_type'] = 0x800;
    }
    if (ipClass == 'Source') 
        tapInfo.fields['nw_src'] = ipStr;
    else if (ipClass == 'Destination') 
        tapInfo.fields['nw_dst'] = ipStr;
    else if (ipClass == 'Src or Dest') 
        tapInfo.fields['nw_host'] = ipStr;

    if (trafficType == 'ARP') {
        tapInfo.fields['dl_type'] = 0x806;
    }

    // Set prerequisite of IPv4 for all other types
    else if (trafficType == 'ICMP') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['nw_proto'] = 1;

    } else if (trafficType == 'TCP') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['nw_proto'] = 6;
    }
    else if (trafficType == 'HTTP') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['nw_proto'] = 6;
        tapInfo.fields['tp_port'] = 80;
    }
    else if (trafficType == 'HTTPS') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['tp_port'] = 443;
        tapInfo.fields['nw_proto'] = 6;
    }
    else if (trafficType == 'UDP') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['nw_proto'] = 0x11;
    }
    else if (trafficType == 'DNS') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['tp_port'] = 53;
        tapInfo.fields['nw_proto'] = 0x11;
    } else if (trafficType == 'DHCP') {
        tapInfo.fields['dl_type'] = 0x800;
        tapInfo.fields['tp_port'] = 67;
        tapInfo.fields['nw_proto'] = 0x11;
    } 

    if(udf_0 != undefined && udf_0 !=""){
        // tapInfo['udf']['udf_0'] = parseInt(udf_0);  
        tapInfo.fields = {}
        tapInfo['fields']['udf0'] = udf_0;    
    }
    if(udf_1 != undefined && udf_1 !=""){
        // tapInfo['udf']['udf_1'] = parseInt(udf_1);
        tapInfo['fields']['udf1'] = udf_1;     
    }
    if(udf_2 != undefined && udf_2 !=""){
        tapInfo['fields']['udf2'] = udf_2;  
    }
    if(udf_3 != undefined && udf_3 !=""){
        tapInfo['fields']['udf3'] = udf_3;     
    }
    console.log(tapInfo.fields);
    return tapInfo;
}

function restoreMain() {
    $("#main").replaceWith(originalMain);
    $('#post-status').html('');
}

function setTap() {
    var tapInfo = makePostData();
    if (tapInfo == undefined)
        return;

    $.post(url.concat("/v1.0/tap/create"), JSON.stringify(tapInfo), function() { 
    }, "json")
    .done(function() {
        originalMain = $('#main').clone();
        $('#post-status').html('');
        $('#main').html('<h2>Tap created</h2><p>Successfully created tap. Check the <a href="/web/stats.html#flow">flow statistics</a> to verify that the rules have been created.</p><button class="pure-button pure-button-primary" onclick="restoreMain()">Create another tap</button>');
    })
    .fail(function() {
        $('#post-status').html('<p style="color:red; background:silver;">Error: Tap creation failed. Please verify your input.');
    });
}


function clearTap() {
    // var tapInfo = makePostData();
    // if (tapInfo == undefined)
    //     return; 
    tapInfo = {}
    tapInfo['dpid'] = $('#switch').val();

    $.post(url.concat("/v1.0/tap/delete"), JSON.stringify(tapInfo), function() { 
    }, "json")
    .done(function() {
        originalMain = $('#main').clone();
        $('#post-status').html('');
        $('#main').html('<h2>Tap deleted</h2><p>Successfully deleted tap. Check the <a href="/web/stats.html#flow">flow statistics</a> to verify that the rules have been deleted.</p><button class="pure-button pure-button-primary" onclick="restoreMain()">Create another tap</button>');
    })
    .fail(function() {
        $('#post-status').html('<p style="color:red; background:silver;">Error: Tap deletion failed. Please verify your input.');
    });
}

updateSwitchList();

function makefirewall_Data() {
    
    var firewallInfo = {};
    firewallInfo['fields']={};
    firewallInfo['actions']={};

    if($('#switch').val()){
        firewallInfo['dpid'] = $('#switch').val();
    }

    if($('#pror').val()){
        firewallInfo['priority'] = parseInt($('#pror').val());
    }


    var in_port = $('#inport').val();

    var dl_vlan = $('#dl_vlan').val();
    var dl_src = $('#dl_src').val();
    var dl_dst = $('#dl_dst').val();

    var arp_spa = $('#arp_spa').val();
    var arp_tpa = $('#arp_tpa').val();
    var nw_src = $('#nw_src').val();
    var nw_dst = $('#nw_dst').val();
    var nw_proto = $('#nw_proto').val();

    var tp_src = $('#tp_src').val();
    var tp_dst = $('#tp_dst').val();

    var normal = $('#normal').is(':checked');
    var drop = $('#drop').is(':checked');

    if(in_port){firewallInfo['fields']['in_port'] = in_port;}

    // if(dl_vlan){firewallInfo['fields']['dl_vlan'] = dl_vlan;}
    if(dl_vlan){firewallInfo['fields']['vlan_vid'] = dl_vlan;}
    // if(dl_src){firewallInfo['fields']['dl_src'] = dl_src;}
    if(dl_src){firewallInfo['fields']['eth_src'] = dl_src;}
    // if(dl_dst){firewallInfo['fields']['dl_dst'] = dl_dst;}
    if(dl_dst){firewallInfo['fields']['eth_dst'] = dl_dst;}

    if(arp_spa){firewallInfo['fields']['arp_spa'] = arp_spa;}
    if(arp_tpa){firewallInfo['fields']['arp_tpa'] = arp_tpa;}
    if(nw_src){firewallInfo['fields']['nw_src'] = nw_src;}
    if(nw_dst){firewallInfo['fields']['nw_dst'] = nw_dst;}
    if(nw_proto){firewallInfo['fields']['nw_proto'] = nw_proto;}



    if(tp_src){firewallInfo['fields']['tp_src'] = parseInt(tp_src);}
    if(tp_dst){firewallInfo['fields']['tp_dst'] = parseInt(tp_dst);}

    if(normal){firewallInfo['actions']['normal'] = 1;}
    if(drop){firewallInfo['actions']['drop'] = 1;}


    return firewallInfo;

}

function setFirewall() {
    var firewallInfo = makefirewall_Data();
    if (firewallInfo == undefined)
        return;
    $.post(url.concat("/v1.0/firewall/create"), JSON.stringify(firewallInfo), function() { 
    }, "json")
    .done(function() {
        originalMain = $('#main').clone();
        $('#post-status').html('');
        $('#main').html('<h2>Tap deleted</h2><p>Successfully set firewall. Check the <a href="/web/stats.html#flow">flow statistics</a> to verify that the rules have been deleted.</p><button class="pure-button pure-button-primary" onclick="restoreMain()">Create another tap</button>');
    })
    .fail(function() {
        $('#post-status').html('<p style="color:red; background:silver;">Error: Firewall set failed. Please verify your input.');
    });
}
function clearFirewall(){
    dpid = $('#switch option:selected').text();
    $.post(url.concat("/v1.0/firewall/clear/"+dpid),function() {})
    .done(function() {
        alert("Firewall Stop");
    })
}