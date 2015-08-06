var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 700 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

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
  .text("Degrees (C)");

function updateChart(ll) {
    var periods = ["lgm", "current", "50", "70"]; // removed "mid"
    var defaultRcp = "85";

    var domain = y.domain();
    var globalMin = 999;
    var globalMax = -999;
    var rescaleAxis = false;

    periods.forEach(function(period, i) {
        url = "/api/" + period + "?lat=" + ll.lat + "&lng=" + ll.lng;
        if (period == "50" || period == "70") {
            url += "&rcp=" + defaultRcp;
        }
        d3.json(url, function(error, d) {
            if (error) throw error;

            if (period != "current") {
                svg.append("path")
                    .datum(d.data)
                    .attr("class", "u" + d.period + " uncertainty clim")
                    .attr("d", area);
            };

            svg.append("path")
                .datum(d.data)
                .attr("class", "m" + d.period + " median clim")
                .attr("d", line);

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
                console.log(y.domain());
                yAxis.scale(y)
                svg.select(".y.axis")
                    .transition()
                    .duration(500)
                    .ease("sin-in-out")
                    .call(yAxis);
                svg.selectAll(".uncertainty").attr("d", area);
                svg.selectAll(".median").attr("d", line);
            };
        });
    });
};

var base = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/{type}/{z}/{x}/{y}.{ext}', {
    type: 'map',
    continuousWorld: false,
    noWrap: true,
    ext: 'jpg',
    attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: '1234'
});

var southWest = L.latLng(-90, -180),
    northEast = L.latLng(90, 180),
    bounds = L.latLngBounds(southWest, northEast);

var map = L.map('map', {
    center: [0, 0],
    zoom: 2,
    maxBounds: bounds,
    layers: [base]
});

var marker;
map.on('click', function(e) {
    if (marker) {
        map.removeLayer(marker);
    }
    d3.selectAll(".clim").remove();
    marker = L.marker(e.latlng.wrap());
    marker.addTo(map);
    updateChart(e.latlng);
});

