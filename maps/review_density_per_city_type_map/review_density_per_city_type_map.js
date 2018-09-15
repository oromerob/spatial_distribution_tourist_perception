var cities = {
    '182_401': { name: 'Las Vegas', center: [36.12132391022011, -115.17354693892297]},
    '191_410': { name: 'Phoenix', center: [33.4921276010644,﻿-111.989647273247]},
    '254_376': { name: 'Madison', center: ﻿[43.0732804686872, -89.404797336763]},
    '258_388': { name: 'Champaign', center:﻿[40.1131094156656, -88.2454785015358]},
    '277_382': { name: 'Cleveland', center:﻿[41.419884872072, -81.6533449693633]},
    '280_404': { name: 'Charlotte', center:﻿[35.2139987534837, -80.8301755849596]},
    '283_386': { name: 'Pittsburgh', center:﻿[40.4434145024169, -79.9784704023696]},
    '284_373': { name: 'Toronto', center:﻿[43.7069197016944, -79.4292026234179]},
    '300_364': { name: 'Montréal', center:﻿[45.5113216264028, -73.614013097276]},
    '498_310': { name: 'Inverness', center:﻿[57.4669637505637, -4.22542674991788]},
    '499_319': { name: 'Edinburgh', center:﻿[55.9510429610808, -3.20057715313665]}
};
var cityTypes = {
    tourist: 'Tourist City',
    shopping: 'Leisure Shopping City',
    nightlife: 'Nightlife City',
    sport: 'Sport City',
    cultural: 'Cultural City',
    historic: 'Historic City',
    business: 'Business City'
};
var userTypes = {
    'all': 'All',
    'locals': 'Locals',
    'visitors': 'Visitors',
    'visitors_proportion': 'Visitor overall',
    'visitors_special': 'Visitors special'
};
var currentCity = '182_401';
var currentCityType = 'tourist';
var currentUserType = 'all';
var currentVisualisationType = 'lineal';
var zoom = 11;
var currentZoom = 15;
var mymap;


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

function citiesSelectInit() {
    var citiesSelect = document.getElementById("cities");
    for(var key in cities) {
        var option = document.createElement("option");
        option.text = cities[key].name;
        option.value = key;
        citiesSelect.add(option);
    }
    citiesSelect.addEventListener("change", function() {
        // LogWrite(citiesSelect.value);
        currentCity = citiesSelect.value;
        mapInit();
    });
    return;
}

function cityTypesSelectInit() {
    var cityTypesSelect = document.getElementById("cityTypes");
    for(var key in cityTypes) {
        var option = document.createElement("option");
        option.text = cityTypes[key];
        option.value = key;
        cityTypesSelect.add(option);
    }
    cityTypesSelect.addEventListener("change", function() {
        // LogWrite(cityTypesSelect.value);
        currentCityType = cityTypesSelect.value;
        mapInit();
    });
    return;
}

function userTypesSelectInit() {
    var userTypesSelect = document.getElementById("userTypes");
    userTypesSelect.addEventListener("change", function() {
        // LogWrite(userTypesSelect.value);
        currentUserType = userTypesSelect.value;
        mapInit();
    });
    return;
}

function visualisationTypesSelectInit() {
    var visualisationTypesSelect = document.getElementById("visualisationTypes");
    visualisationTypesSelect.addEventListener("change", function() {
        // LogWrite(visualisationTypesSelect.value);
        currentVisualisationType = visualisationTypesSelect.value;
        mapInit();
    });
    return;
}

function page_init() {
    zoomSelectInit();
    citiesSelectInit();
    cityTypesSelectInit();
    userTypesSelectInit();
    visualisationTypesSelectInit();
    mapInit();
}

page_init();

function geojsonLoad(callback) {
    var jsonFileName = currentCity + '_z' + currentZoom + '.json';
    loadJSON(jsonFileName, function(response) {
        // Parse JSON string into object
        geojson = JSON.parse(response)[currentCityType];
        callback(geojson);
    });
}

function mapInit() {
    if (mymap != null) {
        mymap.remove()
    }
    geojsonLoad(function(geojson) {
        // LogWrite(geojson);
        map_prepare(geojson, function(getColor, max) {
            mymap = L.map('mapid').setView(cities[currentCity].center, zoom);

            L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                // id: 'mapbox.streets',
                id: 'mapbox.light',
                accessToken: 'pk.eyJ1Ijoib3JvbWVyb2IiLCJhIjoiY2psaTU0cnQwMWtpMzNycXU1am01cXRyaSJ9.ELGdPqv5okQwf6pzT22nKQ'
            }).addTo(mymap);

            var geojsonObject;

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
                // LogWrite('props: ', props);
                this._div.innerHTML = '<h4>' + userTypes[currentUserType] + ' reviews</h4>' +  (props ?
                    props[currentUserType] + ' reviews' : 'Hover over a tile');
            };

            function style(feature) {
                return {
                    fillColor: getColor(feature.properties[currentUserType]),
                    // weight: 2,
                    weight: 1,
                    opacity:
                        feature.properties[currentUserType] < max / 256 && currentVisualisationType === 'exponential' ? 0:
                        feature.properties[currentUserType] < max * 0.111 && currentVisualisationType === 'lineal'? 0:
                        1,
                    color: 'white',
                    dashArray: '3',
                    //fillOpacity: 0.5
                    fillOpacity:
                        feature.properties[currentUserType] < max / 256 && currentVisualisationType === 'exponential' ? 0:
                        feature.properties[currentUserType] < max * 0.111 && currentVisualisationType === 'lineal'? 0:
                        feature.properties[currentUserType] / (max * 2) + 0.3
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
    // LogWrite('currentUserType: ', currentUserType);
    var max = Math.max.apply(Math, geojson.features.map(function(o) { return o.properties[currentUserType]; }));
    // LogWrite('max: ', max);
    function getColor(d) {
        // LogWrite('value: ', d);
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



