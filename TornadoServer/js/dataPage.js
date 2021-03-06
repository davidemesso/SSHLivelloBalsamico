var storicTable   = null;
var realTimeTable = null;

var temperatureChart = null;
var pressureChart    = null;
var humidityChart    = null;
var ws = null;

// Callback to when the page is fully loaded, used to setup the whole page
$(document).ready(() => {
    initJQueryComponents();
    initTables();
    initCharts();
    initWS();
});

function initJQueryComponents()
{
    $('.datepicker').datepicker({
        format: 'yy-mm-dd'
    });

    $('.sidenav').sidenav();
    $('#loaderModal').modal({
	dismissible: false
    });
}

function initTables()
{
    realTimeTable = new DataTable("realtimeDataTable", {
        responsive: true,
        "pageLength": 25,
        "dom": "tp"
    });

    storicTable = new DataTable('dataTable', {
        responsive: true,
        "pageLength": 25
    });
}

function initCharts()
{
    $("#tableContainer").hide();

    temperatureChart = new SensorGraph("temperatureChart");
    pressureChart    = new SensorGraph("pressureChart");
    humidityChart    = new SensorGraph("humidityChart");
}

function initWS()
{
    ws = new WSHandler("ws://balsamico.ssh.edu.it:80/data/ws", wsOnMessage);
}

function wsOnMessage(evt) {
    let data = JSON.parse(evt.data);
    
    if(!Array.isArray(data))
    {   
        temperatureChart.plotData(data, data.temp);
        pressureChart.plotData(data, data.pres);
        humidityChart.plotData(data, data.hum);
        
        data.time = getTimestamp(data.time);
        realTimeTable.addData(data);
    }
    else
    {
        showStoricDataField(data);
	$("#loaderModal").modal("close");
    }
}

function getTimestamp(data)
{
    let d = new Date(0);
    d.setUTCSeconds(data);
    return d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate()+" "+
            d.getHours()+":"+d.getMinutes()+":"+d.getSeconds();
}

function showStoricDataField(data)
{
    $("#tableContainer").show();
    storicTable.clear();
    storicTable.addList(data)
}

function sendStoricDataRequest()
{
    let startTime = $("#startDatePicker").val();
    let endTime = $("#endDatePicker").val();

    let message = {
        type : "StoricDataRequest",
        payload: {
            startTime: startTime,
            endTime: endTime
        }
    }
    
    if(startTime && endTime)
    {
        ws.send(JSON.stringify(message));
    	$("#loaderModal").modal("open");
    }
}

function closeStoricDataField()
{
    storicTable.clear();
    $("#tableContainer").hide();
}
