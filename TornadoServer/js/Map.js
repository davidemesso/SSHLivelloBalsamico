class Map
{
    constructor() 
    {
        this.ostMap = {};
        this.ostMap.markers = []

        this.ostMap.map = L.map('mapContainer');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
            .addTo(this.ostMap.map);

        this.createMarker();
    }

    createMarker()
    {
        return L
            .marker([0, 0])
            .addTo(this.ostMap.map);
    }

    markPositions(list, zoom)
    {
        for(let el of list)
            this.markPosition(el, zoom);
    }

    markPosition(data, zoom)
    {
        let name = data.name;
        let lat = data.lat;
        let long = data.long;
        let volume = data.volume;

        let marker = this.createMarker();

        this.ostMap
            .map
            .setView([lat, long], zoom);
    
        marker
            .setLatLng([lat, long])
            .bindPopup("Name: " + name + "<br>Volume: " + volume + " L")
            .openPopup();

        this.ostMap.markers.push(marker);
    }
}