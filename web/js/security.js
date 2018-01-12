
var url = "http://" + location.hostname + ":8080";
var originalMain;

var portMap = {};

var line_chart_height = $(window).height()/6;
var line_chart_width = $('#tcp_chart_panel').width();


function update_dpid() {
    var switchSelect = document.getElementById("dpid");
    $.getJSON(url.concat("/v1.0/topology/switches"), function(switches){
        $.each(switches, function(index, value){
            var el = document.createElement("option");
            el.textContent = value.dpid;
            el.value = value.dpid;
            switchSelect.appendChild(el);

            portMap[value.dpid] = value.ports;
            if(index == 0){
                get_security_info('0x'+value.dpid);
            }
        });
    });
}
update_dpid();

function get_security_info(dpid) {
    if(!dpid){
        dpid = $('#dpid option:selected').text();
        dpid = '0x'+dpid.replace(/\b(0+)/gi,"");
    }
    $.getJSON(url.concat("/v1.0/security/get/"+dpid), function(data){
        show_chart(data);
    });
}

function security_start(){
    dpid = $('#dpid option:selected').text();
    dpid = dpid.replace(/\b(0+)/gi,"");
    $.post(url.concat("/v1.0/security/start/"+dpid),function() {})
    .done(function() {
        alert("Security Start");
    })
}

function security_stop(){
    dpid = $('#dpid option:selected').text();
    dpid = dpid.replace(/\b(0+)/gi,"");
    $.post(url.concat("/v1.0/security/stop/"+dpid),function() {})
    .done(function() {
        alert("Security Stop");
    })
}

function security_handle(mode,operation){
    dpid = $('#dpid option:selected').text();
    dpid = dpid.replace(/\b(0+)/gi,"");
    $.post(url.concat("/v1.0/security/protect/"+dpid+"/"+mode+"/"+operation),function() {})
    .done(function() {
        alert("Security Handle");
    })
}


function show_chart(data) {
    $('#tcp_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height,
            //  events: {                                                           
            //         load: function() {                                              
                                                                                    
            //             // set up the updating of the chart each second             
            //             var series = this.series[0];                                
            //             setInterval(function() {                                    
            //                 var x = (new Date()).getTime(), // current time         
            //                     y = Math.random();                                  
            //                 series[0].addPoint([x, y], true, true);                    
            //             }, 1000);                                                   
            //         }                                                               
            // }
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'kbps'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['tcp']
        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    $('#dns_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'kbps'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['dns']
        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    $('#udp_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'proportion'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['udp_tcp']
        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    $('#http_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'kbps'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['http']
        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    $('#icmp_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'kbps'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['icmp']
        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    $('#ntp_chart').highcharts({
        chart: {
            zoomType: 'x',
            width:line_chart_width,
            height:line_chart_height
        },
        title: {
            text: null
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'kbps'
            },
            min:0,
            floor:0
        },
        legend: {
            enabled: false
        },
        credits: {
                    enabled: false
        },
        colors: ['#6DC488'],
        series: [{
            type: 'line',
            name: 'packet',
            data: data['ntp']        }] 
        // series: [{
        //     data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //     pointStart: Date.UTC(2010, 0, 1),
        //     pointInterval: 24 * 3600 * 1000 // one day
        // }]
    });
    // function add_point(){
    //     var chart = $('#tcp_chart').highcharts();
    //     setInterval(function() {                                    
    //         var x = (new Date()).getTime(), // current time         
    //             y = Math.random();                                  
    //         chart.series[0].addPoint([x, y]);                    
    //     }, 5000); 
    // }
    // add_point();
}


