var sensorTable = null;
var map = null;
var ws = null;

// Callback to when the page is fully loaded, used to setup the whole page
$(document).ready(() => {
    initJQueryComponents();
    initTable();
    initMap();
    initWS();
    //sendSensorsDataRequest();
});

function initJQueryComponents()
{
    $('.sidenav').sidenav();
}

function initTable()
{
    sensorTable = new DataTable("sensorsDataTable", {
        responsive: true,
        "pageLength": 25,
        "dom": "tp"
    });
}

function initMap()
{
    map = new Map();
}

function initWS()
{
    ws = new WSHandler("ws://balsamico.ssh.edu.it:80/data/ws", wsOnMessage, sendSensorsDataRequest);
}

function wsOnMessage(evt) {
    let data = JSON.parse(evt.data);

    if(Array.isArray(data))
    {
        showSensorsDataField(data);
        map.markPositions(data, 6);
    }
}

function showSensorsDataField(data)
{
    $("#tableContainer").show();
    sensorTable.clear();
    sensorTable.addList(data)
}

function sendSensorsDataRequest()
{
    packet = {
        type : "SensorsDataRequest",
        payload : {}
    };

    ws.send(JSON.stringify(packet));
}
