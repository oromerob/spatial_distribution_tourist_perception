'use strict';

var categories = [
    'All',
    'Monuments',
    'Museums & art galleries',
    'Cinemas & concert & theatres',
    'Nightclubs & bars',
    'Cafés & restaurants',
    'Shops & consumptive activies',
    'Offices & work premises',
    'Sport stadia & events',
    'Public mobility',
    'Private transports'
];
var years = [
    '2017',
    '2016',
    '2015',
    '2014',
    '2013',
    '2012',
    '2011',
    '2010',
    '2009',
    '2008',
    '2007',
    '2006',
    '2005',
    '2004'
];
var currentYear;
var cities;
var currentCity;
var currentCategory;
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
        // logWrite(zoomSelect.value);
        currentZoom = parseInt(zoomSelect.value);
        logWrite('currentZoom: ' + currentZoom);
        zoom = currentZoom === 18 ? 13: 11;
        logWrite('zoom: ' + zoom);
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
        logWrite(areaSelect.value);
        currentCity = areaSelect.value;
        mapInit();
    });
    return;
}

function yearSelectInit() {
    var yearSelect = document.getElementById("year");
    for(var i = 0; i < years.length; i++) {
        var option = document.createElement("option");
        option.text = years[i];
        option.value = years[i];
        yearSelect.add(option);
    }
    yearSelect.addEventListener("change", function() {
        logWrite(yearSelect.value);
        currentYear = yearSelect.value;
        mapInit();
    });
    return;
}

function categorySelectInit() {
    var categorySelect = document.getElementById("category");
    for(var i = 0; i < categories.length; i++) {
        var option = document.createElement("option");
        option.text = categories[i];
        option.value = categories[i];
        categorySelect.add(option);
    }
    categorySelect.addEventListener("change", function() {
        logWrite(categorySelect.value);
        currentCategory = categorySelect.value;
        mapInit();
    });
    return;
}

// function visualisationTypesSelectInit() {
//     var visualisationTypesSelect = document.getElementById("visualisationTypes");
//     visualisationTypesSelect.addEventListener("change", function() {
//         logWrite(visualisationTypesSelect.value);
//         currentVisualisationType = visualisationTypesSelect.value;
//         mapInit();
//     });
//     return;
// }

function page_init() {
    loadJSON('areas.json', function(response) {
        cities = JSON.parse(response);
        currentCity = Object.keys(cities)[0];
        currentCategory = categories[0];
        currentYear = years[0];
        zoomSelectInit();
        areaSelectInit();
        yearSelectInit();
        categorySelectInit();
        // visualisationTypesSelectInit();
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
                mymap.fitBounds(e.target.getBounds());
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
                this._div.innerHTML = '<h4>' + currentCategory + ' - ' + currentYear + '</h4>' +  (props ?
                    props[currentCategory][currentYear] + ' ratio' : 'Hover over a tile');
            };

            function style(feature) {
                return {
                    fillColor: getColor(feature.properties[currentCategory][currentYear]),
                    weight: 0.5,
                    opacity: 0.7,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity:
                        feature.properties[currentCategory][currentYear] > -0.2 * max && feature.properties[currentCategory][currentYear] < 0.2 * max && feature.properties[currentCategory][currentYear] !== 0 ? 0.2:
                        feature.properties[currentCategory][currentYear] === 0 ? 0: 0.5
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
    var max = Math.max.apply(Math, geojson.features.map(function(o) { return Math.abs(o.properties[currentCategory][currentYear]); }));
    function getColor(d) {
        return d > 0.6 * max ? '#84bb56' :
               d > 0.2 * max ? '#c1ca66' :
               d > -0.2 * max ? '#FED976' :
               d > -0.6 * max ? '#FD8D3C' :
                   '#FC4E2A';
        // switch (currentVisualisationType) {
        //     case 'lineal':
        //         var diff = 0.111;
        //         return d > max * diff * 8 ? '#800026' :
        //                d > max * diff * 7 ? '#BD0026' :
        //                d > max * diff * 6 ? '#E31A1C' :
        //                d > max * diff * 5 ? '#FC4E2A' :
        //                d > max * diff * 4 ? '#FD8D3C' :
        //                d > max * diff * 3 ? '#FEB24C' :
        //                d > max * diff * 2 ? '#FED976' :
        //                d > max * diff ? '#FFEDA0' :
        //                           '#ffffff';
        //     case 'exponential':
        //         // every range is half the previous
        //         return d > max / 2 ? '#800026' :
        //                d > max / 4 ? '#BD0026' :
        //                d > max / 8 ? '#E31A1C' :
        //                d > max / 16 ? '#FC4E2A' :
        //                d > max / 32 ? '#FD8D3C' :
        //                d > max / 64 ? '#FEB24C' :
        //                d > max / 128 ? '#FED976' :
        //                d > max / 256 ? '#FFEDA0' :
        //                           '#ffffff';
        // }
    }
    callback(getColor, max);
}

function logWrite(log) {
    console.log(log);
}


