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
var row_width = $('#row-2').width()-20;
var full_height = $(window).height();
var row1_height =$('#os-info').height();


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

function get_dp() {
    var row_1_dpid = document.getElementById("row-1-dpid");
    var row_2_dpid = document.getElementById("row-2-dpid");
    var row_3_dpid = document.getElementById("row-3-dpid");
    $.getJSON(url.concat("/dp_info"), function(switches){
        
        $.each(switches, function(index, value){
        // for(var i = 0; i<switches.length; i++){
            var el1 = document.createElement("option");
            var el2 = document.createElement("option");
            var el3 = document.createElement("option");
            el1.textContent = value;
            el1.value = value;
            el2.textContent = value;
            el2.value = value;
            el3.textContent = value;
            el3.value = value;
            row_1_dpid.appendChild(el1);
            row_2_dpid.appendChild(el2);
            row_3_dpid.appendChild(el3);
        // }
        });
    });
    // }).then(updatePorts);
}
get_dp();

function update_sw_info(){
    var dpid = $('#row-1-dpid option:selected').text().substring(2);
    
    for(var i=0;i<(16-dpid.length);i++){
        dpid = '0'+dpid;
    }

    $.getJSON(url.concat("/stats/desc/").concat(dpid), function(descs){
        $.each(descs, function(key, value){
            $('#sw_model').text(value.hw_desc);
            $('#sw_ver').text(value.sw_desc);
        });
    });
}
update_sw_info();

function update_flow_match(){
    var flow_select = document.getElementById("flow-select");
    $('#flow-select').empty();
    var empty = document.createElement("option");
    empty.textContent = '';
    flow_select.appendChild(empty);
    var dpid = $('#row-3-dpid option:selected').text();
    $.getJSON(url.concat("/flow_type/").concat(dpid), function(flow_type){
        $.each(flow_type, function(index, value){
            var el = document.createElement("option");
            el.textContent = value;
            flow_select.appendChild(el);
        });
    });
}

function update_flow(){
    var flow_match = $('#flow-select option:selected').text();
    $.getJSON(url.concat("/flow_sta/").concat(flow_match), function(flow_traffic){
        $('#flow_byte').highcharts({
            chart: {
                zoomType: 'x',
                width:row_width/2,
                height:full_height/4
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
                            [0, '#F65926']
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
            colors: ['#F65926'],
            series: [{
                type: 'area',
                name: 'byte',
                data: flow_traffic['byte']
            }] 
        });
        $('#flow_packet').highcharts({
            chart: {
                zoomType: 'x',
                width:row_width/2,
                height:full_height/4
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
                            [0, '#F65926']
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
            colors: ['#F65926'],
            series: [{
                type: 'area',
                name: 'packet',
                data: flow_traffic['packet']
            }] 
        });
    });

}

function get_controller_info(){
    $.getJSON(url.concat("/controller_info"), function(ctr_info){
        $('#ctr_ip').text(window.location.hostname);
        $('#ctr_cpu').text(ctr_info.cpu_load+'%');
        $('#ctr_disk').text(ctr_info.disk_load+'%');
        $('#ctr_mem').text(ctr_info.mem_load+'%');

        $('#cpu-chart').highcharts({
            chart: {
                height:row1_height,
                width:row1_height,
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false
            },
            title: {
                text: 'CPU'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    }
                }
            },
            credits: {
                enabled: false
            },
            colors: ['#F65926','#231F20'],
            series: [{
                type: 'pie',
                name: 'Proportion',
                data: [
                    ['Used', ctr_info.cpu_load],
                    ['Free',   Math.ceil(ctr_info.cpu_load/100)*100 -ctr_info.cpu_load]
                ]
            }]
        });
        // $('#disk-chart').highcharts({
        //     chart: {
        //         height:row1_height,
        //         width:row1_height,
        //         plotBackgroundColor: null,
        //         plotBorderWidth: null,
        //         plotShadow: false
        //     },
        //     title: {
        //         text: 'Disk'
        //     },
        //     tooltip: {
        //         pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        //     },
        //     plotOptions: {
        //         pie: {
        //             allowPointSelect: true,
        //             cursor: 'pointer',
        //             dataLabels: {
        //                 enabled: false
        //             }
                    
        //         }
        //     },
        //     credits: {
        //         enabled: false
        //     },
        //     colors: ['#F65926','#231F20'],
        //     series: [{
        //         type: 'pie',
        //         name: 'Proportion',
        //         data: [
        //             ['Used', ctr_info.disk_load],
        //             ['Free',   100-ctr_info.disk_load]
        //         ]
        //     }]
        // });
        // $('#memory-chart').highcharts({
        //     chart: {
        //         height:row1_height,
        //         width:row1_height,
        //         plotBackgroundColor: null,
        //         plotBorderWidth: null,
        //         plotShadow: false
        //     },
        //     title: {
        //         text: 'Memory'
        //     },
        //     tooltip: {
        //         pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        //     },
        //     plotOptions: {
        //         pie: {
        //             allowPointSelect: true,
        //             cursor: 'pointer',
        //             dataLabels: {
        //                 enabled: false
        //             }
                    
        //         }
        //     },
        //     credits: {
        //         enabled: false
        //     },
        //     colors: ['#F65926','#231F20'],
        //     series: [{
        //         type: 'pie',
        //         name: 'Proportion',
        //         data: [
        //             // {
        //             //     name: 'Used',
        //             //     y: ctr_info.mem_load,
        //             //     sliced: true,
        //             //     selected: true
        //             // },
        //             ['Used', ctr_info.mem_load],
        //             ['Free',   100-ctr_info.mem_load]
        //         ]
        //     }]
        // });
    });
}
get_controller_info();

function updata_sw_traffic(){
    var dpid = $('#row-2-dpid option:selected').text();
    $.getJSON(url.concat("/switch_sta/").concat(dpid), function(sw_traffic){
        $('#input').highcharts({
            chart: {
                zoomType: 'x',
                width:row_width/3,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: 'Input'
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
                            [0, '#F65926']
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
            colors: ['#F65926'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['input']
            }]
        });

        $('#output').highcharts({
            chart: {
                zoomType: 'x',
                width:row_width/3,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: 'Output'
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
                            [0, '#F65926']
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
            colors: ['#F65926'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['output']
            }]
        });
        $('#drop').highcharts({
            chart: {
                zoomType: 'x',
                width:row_width/3,
                height:full_height/4
                // height: chart_height
            },
            title: {
                text: 'Drop'
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
                            [0, '#F65926']
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
            colors: ['#F65926'],
            series: [{
                type: 'area',
                name: 'Flow',
                data: sw_traffic['drop']
            }]
        });
    });
}
updata_sw_traffic(); 

$(function () {
    $('#flow-chart').highcharts({
        chart: {
            height:row1_height,
            width:row1_height,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: 'Flow Usage'
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                }
            }
        },
        credits: {
            enabled: false
        },
        colors: ['#F65926','#231F20'],
        series: [{
            type: 'pie',
            name: 'Proportion',
            data: [
                ['Used', 20],
                ['Free', 80]
            ]
        }]
    });
    
    // $.getJSON('https://www.highcharts.com/samples/data/jsonp.php?filename=usdeur.json&callback=?', function (data) {
        
    // });
});

