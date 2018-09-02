function loadJSON(filename, callback) {

    var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
    xobj.open('GET', filename, true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);
}

function init() {
    loadJSON('182_401_business_z15.json', function(response) {
        // Parse JSON string into object
        geojson = { "type": "FeatureCollection", "features": JSON.parse(response) };
        console.log(geojson);
        map_init(geojson);
    });
}

init();

function map_init(geojson) {
    map_prepare(geojson, function(getColor, max) {
        var mymap = L.map('mapid').setView([36.12132391022011, -115.17354693892297], 11);

        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            // id: 'mapbox.streets',
            id: 'mapbox.light',
            accessToken: 'pk.eyJ1Ijoib3JvbWVyb2IiLCJhIjoiY2psaTU0cnQwMWtpMzNycXU1am01cXRyaSJ9.ELGdPqv5okQwf6pzT22nKQ'
        }).addTo(mymap);

        function highlightFeature(e) {
            var layer = e.target;

            layer.setStyle({
                weight: 5,
                color: '#666',
                dashArray: '',
                fillOpacity: 0.7
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                layer.bringToFront();
            }
            info.update(layer.feature.properties);
        }

        function resetHighlight(e) {
            geojson.resetStyle(e.target);
            info.update();
        }

        function zoomToFeature(e) {
            map.fitBounds(e.target.getBounds());
        }

        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            });
        }


        var info = L.control();

        info.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
            this.update();
            return this._div;
        };

        // method that we will use to update the control based on feature properties passed
        info.update = function (props) {
            this._div.innerHTML = '<h4>Tile Venue Density</h4>' +  (props ?
                props.venues + ' venues' : 'Hover over a tile');
        };

        function style(feature) {
            return {
                fillColor: getColor(feature.properties.venues),
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                //fillOpacity: 0.5
                fillOpacity: feature.properties.venues / (max * 2) + 0.2
            };
        }

        info.addTo(mymap);

        L.geoJSON(geojson, {
            style: style,
            onEachFeature: onEachFeature
        }).addTo(mymap);

    })


}

function map_prepare(geojson, callback) {
    var max = Math.max.apply(Math, geojson.features.map(function(o) { return o.properties.venues; }));
    function getColor(d) {
        var diff = 0.143
        return d > max * diff * 7 ? '#800026' :
               d > max * diff * 6  ? '#BD0026' :
               d > max * diff * 5  ? '#E31A1C' :
               d > max * diff * 4  ? '#FC4E2A' :
               d > max * diff * 3   ? '#FD8D3C' :
               d > max * diff * 2   ? '#FEB24C' :
               d > max * diff * 1   ? '#FED976' :
                          '#FFEDA0';
        /*
        var diff = 0.125
        return d > max * diff * 8 ? '#800026' :
               d > max * diff * 7  ? '#BD0026' :
               d > max * diff * 6  ? '#E31A1C' :
               d > max * diff * 5  ? '#FC4E2A' :
               d > max * diff * 4   ? '#FD8D3C' :
               d > max * diff * 3   ? '#FEB24C' :
               d > max * diff * 2   ? '#FED976' :
               d > max * diff * 1   ? '#FFEDA0' :
                          '#FFFFFF';
        */

        /*
        return d > max * 0.8 ? '#800026' :
               d > max * 0.7  ? '#BD0026' :
               d > max * 0.6  ? '#E31A1C' :
               d > max * 0.5  ? '#FC4E2A' :
               d > max * 0.4   ? '#FD8D3C' :
               d > max * 0.3   ? '#FEB24C' :
               d > max * 0.2   ? '#FED976' :
               d > max * 0.1   ? '#FFEDA0' :
                          '#FFFFFF';
        */

        /*
        return d > max * 0.7 ? '#800026' :
               d > max * 0.6  ? '#BD0026' :
               d > max * 0.5  ? '#E31A1C' :
               d > max * 0.4  ? '#FC4E2A' :
               d > max * 0.3   ? '#FD8D3C' :
               d > max * 0.2   ? '#FEB24C' :
               d > max * 0.1   ? '#FED976' :
                          '#FFEDA0';
        */

        /*
        // every range is half the previous
        return d > max / 2 ? '#800026' :
               d > max / 4  ? '#BD0026' :
               d > max / 8  ? '#E31A1C' :
               d > max / 16  ? '#FC4E2A' :
               d > max / 32   ? '#FD8D3C' :
               d > max / 64   ? '#FEB24C' :
               d > max / 128   ? '#FED976' :
                          '#FFEDA0';
        */

    }

    callback(getColor, max);
}






