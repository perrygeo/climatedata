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
    .interpolate("basis")
    .x(function(d) { return x(d.month); })
    .y1(function(d) { return y(d.max); })
    .y0(function(d) { return y(d.min); });

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

x.domain([1, 12])
y.domain([-20, 50]);

svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis);

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
    url = "/api?lat=" + ll.lat + "&lng=" + ll.lng;
    d3.json(url, function(error, data) {
      if (error) throw error;
      data.results.forEach(function(d, i) {
          svg.append("path")
              .datum(d.data)
              .attr("class", d.period + " cloud")
              .attr("d", area);
      });
    });
    // TODO remove loading
};

var base = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/{type}/{z}/{x}/{y}.{ext}', {
    type: 'map',
    ext: 'jpg',
    attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: '1234'
});

var map = L.map('map', {
    center: [0, 0],
    zoom: 1,
    layers: [base]
});

var marker;
map.on('click', function(e) {
    if (marker) {
        map.removeLayer(marker);
    }
    d3.selectAll(".cloud").remove();
    marker = L.marker(e.latlng);
    marker.addTo(map);
    // TODO loading
    updateChart(e.latlng);
});

