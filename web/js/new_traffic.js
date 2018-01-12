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
// var row_width = $('#row-2').width()-20;

// var sw_info_width =$('#input_col').width()-30;
var sw_info_width =$('#sw_show').width()-30;
var flow_info_width = $('#flow_info').width()-30;
var full_height = $(window).height();


var flow_info_height = $('#sw_info_row').height()+full_height/4+30;

var overview_width = $('#overview_info').width();
var overview_height = $('#controller_info').height();

var flow_chart_height = $('#sw_info').height();




// $('#sys-info').width($('#row-2').width()-$('#os-info').width());


// var line_height = $("#input-table").outerHeight(true)+12;
// var flow_select_height = $("#flow-select").outerHeight(true);
// var chart_height = line_height-flow_select_height-30;
// $('#chart-part').css('height',line_height+'px');

// function updateSwitchList() {
//     var switchSelect = document.getElementById("switch");
//     $.getJSON(url.concat("/v1.0/topology/switches"), function(switches){
//         $.each(switches, function(index, value){
//             var el = document.createElement("option");
//             el.textContent = value.dpid;
//             el.value = value.dpid;
//             switchSelect.appendChild(el);

//             portMap[value.dpid] = value.ports;
//         });
//     }).then(updatePorts);
// }
var sw_show_turns =0;
$('#output').hide();
$('#drop').hide();
function sw_show(){
    sw_show_turns++;
    if(sw_show_turns == 1){
        $('#input').show(1000);
        $('#drop').hide(1000);
    }
    if(sw_show_turns == 2){
        $('#input').hide(1000);
        $('#output').show(1000);
    }
    if(sw_show_turns == 3){
        $('#output').hide(1000);
        $('#drop').show(1000);
        sw_show_turns = 0;
    }

}
$(document).ready(function(){  
    var sw_timer=setInterval(sw_show, 5000);
    $("#sw_show").mouseover(function(){
        clearInterval(sw_timer);
    });
    $("#sw_show").mouseout(function(){
        sw_timer =setInterval(sw_show, 5000);
    });  
});  

function get_dp() {
    var dpid = document.getElementById("dpid");
    $.getJSON(url.concat("/dp_info"), function(switches){
        
        $.each(switches, function(index, value){
            var el = document.createElement("option");
            el.textContent = value;
            el.value = value;
            if(index == 0){
                $(el).attr("selected='selected'");
                updata_sw_traffic(value);
                update_sw_info(value.substring(2));
                update_flow_match(value);
            }
            dpid.appendChild(el);
        });
    });
}
get_dp();

function get_overview(){
    $.getJSON(url.concat("/overview"), function(overview){
        
        $('#overview_chart').highcharts({
            chart: {
                type: 'column',
                width:overview_width,
                height:overview_height
            },
            legend: {
                enabled:false
            },
            xAxis: {
                categories: overview['dp']
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'KBPS'
                }
            },
            plotOptions: {
                series: {
                    dataLabels: {
                        enabled: true
                    }
                }
            },
            title: {
                text: null
            },
            // tooltip: {
            //     headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            //     pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            //         '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            //     footerFormat: '</table>',
            //     shared: true,
            //     useHTML: true
            // },
            // plotOptions: {
            //     column: {
            //         pointPadding: 0.2,
            //         borderWidth: 0
            //     }
            // },
            credits: {
                enabled: false
            },
            colors: ['#6DC488','#ECCE70','#636366'],
            series: [{
                name: 'Input',
                data: overview['input']
            }, {
                name: 'Output',
                data: overview['output']
            }, {
                name: 'Drop',
                data: overview['drop']
            }]
        });
    });
}
get_overview();

function update_sw_info(dpid){
    if(typeof(dpid)=='undefined'){
        dpid = $('#dpid option:selected').text().substring(2);
    }
    for(var i=0;i<(16-dpid.length);i++){
        dpid = '0'+dpid;
    }

    $.getJSON(url.concat("/stats/desc/").concat(dpid), function(descs){
        $.each(descs, function(key, value){
            $('#sw_model').text(value.hw_desc);
            $('#sw_ver').text(value.sw_desc);
        });
    });
    $.getJSON(url.concat("/stats/flow/").concat(dpid), function(flows){
        $('#sw_flow_num').text(flows[dpid].length);
    });
    $.getJSON(url.concat("/stats/port/").concat(dpid), function(ports) {
        $('#sw_port_num').text(ports[dpid].length-1);
    });
}
// update_sw_info();

function update_flow_match(dpid){
    if(!dpid){
        var dpid = $('#dpid option:selected').text();
    }
    var flow_select = document.getElementById("flow-select");
    $('#flow-select').empty();
    // var empty = document.createElement("option");
    // empty.textContent = '';
    // flow_select.appendChild(empty);
    
    $.getJSON(url.concat("/flow_type/").concat(dpid), function(flow_type){
        $.each(flow_type, function(index, value){
            var el = document.createElement("option");
            el.textContent = value;
            flow_select.appendChild(el);
            if(index == 0){
                update_flow(value);
            }
        });
    });
}

function update_flow(flow_match){
    if(!flow_match){
        var flow_match = $('#flow-select option:selected').text();
    }
    $.getJSON(url.concat("/flow_sta/").concat(flow_match), function(flow_traffic){
        $('#flow_byte').highcharts({
            chart: {
                zoomType: 'x',
                width:flow_info_width,
                height:flow_info_height/2
                // height: chart_height
            },
            title: {
                text: 'Flow Byte'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'KBPS'
                },
                min:0,
                floor:0
            },
            legend: {
                enabled: false
            },
            // plotOptions: {
            //     area: {
            //         fillColor: {
            //             linearGradient: {
            //                 x1: 0,
            //                 y1: 0,
            //                 x2: 0,
            //                 y2: 1
            //             },
            //             stops: [
            //                 // [0, Highcharts.getOptions().colors[0]],
            //                 // [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
            //                 [0, '#F65926']
            //                 // [1, Highcharts.Color('#F65926').setOpacity(0).get('rgba')]
            //             ]
            //         },
            //         marker: {
            //             radius: 2
            //         },
            //         lineWidth: 1,
            //         states: {
            //             hover: {
            //                 lineWidth: 1
            //             }
            //         },
            //         threshold: null
            //     }
            // },
            credits: {
                enabled: false
            },
            colors: ['#ECCE70'],
            // colors: ['#F65926'],
            series: [{
                // type: 'area',
                type: 'line',
                name: 'byte',
                data: flow_traffic['byte']
            }] 
        });
        $('#flow_packet').highcharts({
            chart: {
                zoomType: 'x',
                width:flow_info_width,
                height:flow_info_height/2
                // height: chart_height
            },
            title: {
                text: 'Flow Packet'
            },
            // subtitle: {
            //     text: document.ontouchstart === undefined ?
            //             'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            // },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'KBPS'
                },
                min:0,
                floor:0
            },
            legend: {
                enabled: false
            },
            // plotOptions: {
            //     area: {
            //         fillColor: {
            //             linearGradient: {
            //                 x1: 0,
            //                 y1: 0,
            //                 x2: 0,
            //                 y2: 1
            //             },
            //             stops: [
            //                 // [0, Highcharts.getOptions().colors[0]],
            //                 // [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
            //                 [0, '#6DC488']
            //                 // [1, Highcharts.Color('#F65926').setOpacity(0).get('rgba')]
            //             ]
            //         },
            //         marker: {
            //             radius: 2
            //         },
            //         lineWidth: 1,
            //         states: {
            //             hover: {
            //                 lineWidth: 1
            //             }
            //         },
            //         threshold: null
            //     }
            // },
            credits: {
                        enabled: false
            },
            // colors: ['#F65926'],
            colors: ['#6DC488'],
            series: [{
                type: 'line',
                name: 'packet',
                data: flow_traffic['packet']
            }] 
        });
    });

}

function get_controller_info(){
    $.getJSON(url.concat("/controller_info"), function(ctr_info){

        var percent_cpu = parseInt((ctr_info.cpu_load/(Math.ceil(ctr_info.cpu_load/100)*100))*100);
        var percent_hd = parseInt(ctr_info.disk_load);
        var percent_ram = parseInt(ctr_info.mem_load);
        
        $('#ctr_ip').text(window.location.hostname);
        $('#progress_cpu').text(percent_cpu+'%').css('width',percent_cpu+'%');
        $('#progress_hd').text(percent_hd+'%').css('width',percent_hd+'%');
        $('#progress_ram').text(percent_ram+'%').css('width',percent_ram+'%');

        if(percent_cpu<=65){
            $('#progress_cpu').css('background-color','#6DC488');
        }else if(percent_cpu<=85){
            $('#progress_cpu').css('background-color','#ECCE70');
        }else{
            $('#progress_cpu').css('background-color','#FF1919');
        }

        if(percent_hd<=65){
            $('#progress_hd').css('background-color','#6DC488');
        }else if(percent_hd<=85){
            $('#progress_hd').css('background-color','#ECCE70');
        }else{
            $('#progress_hd').css('background-color','#FF1919');
        }

        if(percent_ram<65){
            $('#progress_ram').css('background-color','#6DC488');
        }else if(percent_ram<85){
            $('#progress_ram').css('background-color','#ECCE70');
        }else{
            $('#progress_ram').css('background-color','#FF1919');
        }
       
    });
}
get_controller_info();

function updata_sw_traffic(dpid){
    if(!dpid){
        var dpid = $('#dpid option:selected').text();
    }
    $.getJSON(url.concat("/switch_sta/").concat(dpid), function(sw_traffic){
        $('#input').highcharts({
            chart: {
                zoomType: 'x',
                width:sw_info_width,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: "Input"
            },
            // subtitle: {
            //     text: document.ontouchstart === undefined ?
            //             'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            // },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'KBPS'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            // [0, Highcharts.getOptions().colors[0]],
                            // [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                            [0, '#6DC488']
                            // [1, Highcharts.Color('#F65926').setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },
            credits: {
                        enabled: false
            },
            colors: ['#6DC488'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['input']
            }]
        });

        $('#output').highcharts({
            chart: {
                zoomType: 'x',
                width:sw_info_width,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: "Output"
            },
            // subtitle: {
            //     text: document.ontouchstart === undefined ?
            //             'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            // },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'KBPS'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            // [0, Highcharts.getOptions().colors[0]],
                            // [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                            [0, '#ECCE70']
                            // [1, Highcharts.Color('#F65926').setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },
            credits: {
                        enabled: false
            },
            colors: ['#ECCE70'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['output']
            }]
        });
        $('#drop').highcharts({
            chart: {
                zoomType: 'x',
                width:sw_info_width,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: "Drop"
            },
            // subtitle: {
            //     text: document.ontouchstart === undefined ?
            //             'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            // },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'KBPS'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            // [0, Highcharts.getOptions().colors[0]],
                            // [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                            [0, '#636366']
                            // [1, Highcharts.Color('#F65926').setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },
            credits: {
                        enabled: false
            },
            colors: ['#636366'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['drop']
            }]
        });
    });
}
// updata_sw_traffic(); 


