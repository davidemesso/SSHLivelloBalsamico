class WSHandler{
    constructor(url, callback, open = function(){})
    {
        this.ws = new WebSocket(url);
        this.ws.onmessage = callback;
	this.ws.onopen    = open;
    }

    send(data)
    {
        this.ws.send(data);
    }
}
