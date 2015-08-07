
var timestamp;
var defaultRcp = "85";
var units = "F";
var variable = "tx"; // tn, pr

// D3.js
var margin = {top: 10, right: 80, bottom: 30, left: 50},
    width = 560 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var area = d3.svg.area()
    .interpolate("cardinal")
    .x(function(d) { return x(d.month); })
    .y1(function(d) { return y(d.max); })
    .y0(function(d) { return y(d.min); });

var line = d3.svg.line()
    .interpolate("cardinal")
    .x(function(d) { return x(d.month); })
    .y(function(d) { return y(d.median); });

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

x.domain([1, 12]);
y.domain([-20, 50]);

svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis)
.append("text")
  .attr("x", width)
  .attr("dy", "-.31em")
  .style("text-anchor", "end")
  .text("Month");

svg.append("g")
  .attr("class", "y axis")
  .call(yAxis)
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", ".71em")
  .style("text-anchor", "end")
  .text("Degrees ("+ units + ")");

function label(d) {
    var last = d[d.length - 1];
    return y(last.median);
}

function periodLookup(p) {
    var periods = {
        "current": "1950-2000",
        "lgm": "~20000 BC",
        "50": "2040-2060",
        "70": "2060-2080",
        "mid": "~4000 BC"
    }
    return periods[p];
}

function updateChart(ll) {
    var periods = ["current", "lgm", "50", "70", "mid"];

    var domain = y.domain();
    var globalMin = 999;
    var globalMax = -999;
    var rescaleAxis = false;

    timestamp = Date.now();

    periods.forEach(function(period, i) {
        url = "/api/" + variable + "/" + period + "?lat=" + ll.lat + "&lng=" + ll.lng;
        url += "&timestamp=" + timestamp + "&units=" + units;
        if (period == "50" || period == "70") {
            url += "&rcp=" + defaultRcp;
        }
        d3.json(url, function(error, d) {
            if (error) {
                return false;
            }
            if (d.timestamp != timestamp) {
                console.log("timestamps don't match; discard");
                return false;
            };

            if (period != "current") {
                svg.append("path")
                    .datum(d.data)
                    .attr("class", "period-" + d.period + " uncertainty clim")
                    .attr("d", area);
            };

            svg.append("path")
                .datum(d.data)
                .attr("class", "period-" + d.period + " median clim")
                .attr("d", line)

            svg.append("text")
                .datum(d.data)
                .attr("y", label)
                .attr("x", width)
                .attr("dx", ".21em")
                .style("text-anchor", "start")
                .attr("class", "period-" + d.period + " label clim")
                .text(periodLookup(d.period));

            if (d.min < globalMin) {
                globalMin = d.min;
                rescaleAxis = true;
            }
            if (d.max > globalMax) {
                globalMax = d.max;
                rescaleAxis = true;
            }
            if (rescaleAxis) {
                y.domain([globalMin, globalMax]);
                yAxis.scale(y)
                svg.select(".y.axis")
                    .transition().duration(500).ease("sin-in-out")
                    .call(yAxis);
                svg.selectAll(".uncertainty")
                    .transition().duration(500).ease("sin-in-out")
                    .attr("d", area);
                svg.selectAll(".median")
                    .transition().duration(500).ease("sin-in-out")
                    .attr("d", line);
                svg.selectAll(".label")
                    .transition().duration(500).ease("sin-in-out")
                    .attr("y", label)
            };
        });
    });
};

L.mapbox.accessToken = 'pk.eyJ1IjoicGVycnlnZW8iLCJhIjoiNjJlNTZmNTNjZTFkZTE2NDUxMjg2ZDg2ZDdjMzI5NTEifQ.-f-A9HuHrPZ7fHhlZxYLHQ';

var map = L.mapbox.map('map', 'mapbox.outdoors')
    .setView([0, 0], 1);

var geocoderControl = L.mapbox.geocoderControl('mapbox.places');
geocoderControl.addTo(map);

var marker;
var coordinates = document.getElementById('coordinates');
map.on('click', function(e) {
    if (marker) {
        map.removeLayer(marker);
    }
    d3.selectAll(".clim").remove();
    marker = L.marker(e.latlng.wrap());
    marker.addTo(map);
    coordinates.innerHTML = 'Latitude: ' + e.latlng.lat + ' Longitude: ' + e.latlng.lng;
    updateChart(e.latlng);
});

