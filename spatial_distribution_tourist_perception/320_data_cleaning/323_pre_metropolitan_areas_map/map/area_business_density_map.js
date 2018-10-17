'use strict';

var cities;
var currentCity;
var currentVisualisationType = 'lineal';
var zoom = 11;
var currentZoom = 15;
var mymap;


function loadJSON(filename, callback) {
    var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
    xobj.open('GET', '../data/' + filename, true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);
}

function zoomSelectInit() {
    var zoomSelect = document.getElementById("zoom");
    zoomSelect.addEventListener("change", function() {
        // LogWrite(zoomSelect.value);
        currentZoom = parseInt(zoomSelect.value);
        LogWrite('currentZoom: ' + currentZoom);
        zoom = currentZoom === 18 ? 13: 11;
        LogWrite('zoom: ' + zoom);
        mapInit();
    });
    return;
}

function areaSelectInit() {
    var areaSelect = document.getElementById("area");
    for(var key in cities) {
        var option = document.createElement("option");
        option.text = cities[key].name;
        option.value = key;
        areaSelect.add(option);
    }
    areaSelect.addEventListener("change", function() {
        console.log(areaSelect.value);
        currentCity = areaSelect.value;
        mapInit();
    });
    return;
}

function visualisationTypesSelectInit() {
    var visualisationTypesSelect = document.getElementById("visualisationTypes");
    visualisationTypesSelect.addEventListener("change", function() {
        console.log(visualisationTypesSelect.value);
        currentVisualisationType = visualisationTypesSelect.value;
        mapInit();
    });
    return;
}

function page_init() {
    loadJSON('areas.json', function(response) {
        cities = JSON.parse(response);
        currentCity = Object.keys(cities)[0];
        zoomSelectInit();
        areaSelectInit();
        visualisationTypesSelectInit();
        mapInit();
    });
}

page_init();

function geojsonLoad(callback) {
    var jsonFileName = currentCity + '_z' + currentZoom +'.json';
    loadJSON(jsonFileName, function(response) {
        // Parse JSON string into object
        var geojson = JSON.parse(response);
        callback(geojson);
    });
}

function mapInit() {
    if (mymap != null) {
        mymap.remove()
    }
    geojsonLoad(function(geojson) {
        map_prepare(geojson, function(getColor, max) {
            mymap = L.map('mapid').setView(cities[currentCity].center, zoom);

            L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                id: 'mapbox.light',
                accessToken: 'pk.eyJ1Ijoib3JvbWVyb2IiLCJhIjoiY2psaTU0cnQwMWtpMzNycXU1am01cXRyaSJ9.ELGdPqv5okQwf6pzT22nKQ'
            }).addTo(mymap);

            var geojsonObject;

            function highlightFeature(e) {
                var layer = e.target;

                layer.setStyle({
                    weight: 3,
                    color: '#666',
                    dashArray: '',
                    fillOpacity: 0.8
                });

                if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                    layer.bringToFront();
                }
                info.update(layer.feature.properties);
            }

            function resetHighlight(e) {
                geojsonObject.resetStyle(e.target);
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
                this._div.innerHTML = '<h4>Business</h4>' +  (props ?
                    props.business + ' business' : 'Hover over a tile');
            };

            function style(feature) {
                return {
                    fillColor: getColor(feature.properties.business),
                    weight: 0.5,
                    opacity:
                        feature.properties.business < max / 256 && currentVisualisationType === 'exponential' ? 0:
                        feature.properties.business < max * 0.111 && currentVisualisationType === 'lineal'? 0:
                        1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity:
                        feature.properties.business < max / 256 && currentVisualisationType === 'exponential' ? 0:
                        feature.properties.business < max * 0.111 && currentVisualisationType === 'lineal'? 0:
                        feature.properties.business / (max * 2) + 0.3
                        // 0.5
                };
            }

            info.addTo(mymap);

            geojsonObject = L.geoJSON(geojson, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(mymap);
        })
    })
}

function map_prepare(geojson, callback) {
    var max = Math.max.apply(Math, geojson.features.map(function(o) { return o.properties.business; }));
    function getColor(d) {
        switch (currentVisualisationType) {
            case 'lineal':
                var diff = 0.111;
                return d > max * diff * 8 ? '#800026' :
                       d > max * diff * 7 ? '#BD0026' :
                       d > max * diff * 6 ? '#E31A1C' :
                       d > max * diff * 5 ? '#FC4E2A' :
                       d > max * diff * 4 ? '#FD8D3C' :
                       d > max * diff * 3 ? '#FEB24C' :
                       d > max * diff * 2 ? '#FED976' :
                       d > max * diff ? '#FFEDA0' :
                                  '#ffffff';
            case 'exponential':
                // every range is half the previous
                return d > max / 2 ? '#800026' :
                       d > max / 4 ? '#BD0026' :
                       d > max / 8 ? '#E31A1C' :
                       d > max / 16 ? '#FC4E2A' :
                       d > max / 32 ? '#FD8D3C' :
                       d > max / 64 ? '#FEB24C' :
                       d > max / 128 ? '#FED976' :
                       d > max / 256 ? '#FFEDA0' :
                                  '#ffffff';
        }
    }
    callback(getColor, max);
}

function LogWrite(log) {
    console.log(log);
}


