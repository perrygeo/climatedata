
var timestamp;
var rcp = "85";
var units = "F";
var variable = "tx"; // tn, pr
var duration = 500;
var ease = 'quad-out'; // "sin-in-out";

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

// Initial note
svg.append("text")
  .attr("y", height/2)
  .attr("x", width/2)
  .attr("class", "initnote")
  .style("text-anchor", "middle")
  .text("Click map to select location");

// // append the rectangle to capture mouse
// svg.append("rect")
//     .attr("width", width)
//     .attr("height", height)
//     .style("fill", "none")
//     .style("pointer-events", "all")
//     .on("mouseover", function() { focus.style("display", null); })
//     .on("mouseout", function() { focus.style("display", "none"); })
//     .on("mousemove", mousemove);

// function mousemove() {
//     var x0 = x.invert(d3.mouse(this)[0]),
//         i = bisectDate(data, x0, 1),
//         d0 = data[i - 1],
//         d1 = data[i],
//         d = x0 - d0.date > d1.date - x0 ? d1 : d0;

//     focus.select("circle.y")
//         .attr("transform",
//                 "translate(" + x(d.date) + "," +
//                                 y(d.close) + ")");
// }

svg.append("g")
  .attr("class", "y axis")
  .call(yAxis)
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", ".71em")
  .attr("class", "ylabel")
  .style("text-anchor", "end")
  .text("Degrees ("+ units + ")");

d3.select("#selectVariable").on("change", function(){
    variable = this.value;
    d3.select(".ylabel").text(labelLookup(variable));
    if (currentLatLng) {
        d3.selectAll(".clim").remove();
        updateChart(currentLatLng, false);
    }
});

d3.select("#selectRcp").on("change", function(){
    rcp = this.value;
    if (currentLatLng) {
        d3.selectAll(".clim.period-50").remove();
        d3.selectAll(".clim.period-70").remove();
        updateChart(currentLatLng, true);
    }
});

function label(d) {
    var last = d[d.length - 1];
    return y(last.median);
}

function labelLookup(x) {
    var labels = {
        "tn": "Degrees ("+ units + ")",
        "tx": "Degrees ("+ units + ")",
        "pr": "Precipitation (mm)"
    }
    return labels[x];
}

function updateChart(ll, futureOnly) {
    if (futureOnly === undefined) {
        futureOnly = false;
    }
    var periods = ["current", "mid", "70"]; // "50" , "lgm"];

    var domain = y.domain();
    var globalMin = 999;
    var globalMax = -999;

    timestamp = Date.now();

    d3.select(".initnote").remove();

    periods.forEach(function(period, i) {
        url = "/api/" + variable + "/" + period + "?lat=" + ll.lat + "&lng=" + ll.lng;
        url += "&timestamp=" + timestamp + "&units=" + units;
        if (period == "50" || period == "70") {
            url += "&rcp=" + rcp;
        } else {
            if (futureOnly) return;
        }

        d3.selectAll(".label.period-" + period).classed("loading-period", true);

        d3.json(url, function(error, d) {
            if (error) {
                return false;
            }
            if (d.timestamp != timestamp) {
                console.log("timestamps don't match; discard");
                return false;
            };
            var rescaleAxis = false;

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

            d3.select(".label.period-" + d.period).classed("loading-period", false);

            if (d.min < globalMin) {
                globalMin = d.min;
                rescaleAxis = true;
            }
            if (d.max > globalMax) {
                globalMax = d.max;
                rescaleAxis = true;
            }
            if (rescaleAxis && !futureOnly) {
                y.domain([globalMin, globalMax]);
                yAxis.scale(y)
                svg.select(".y.axis")
                    .transition().duration(duration).ease(ease)
                    .call(yAxis);
                svg.selectAll(".uncertainty")
                    .transition().duration(duration).ease(ease)
                    .attr("d", area);
                svg.selectAll(".median")
                    .transition().duration(duration).ease(ease)
                    .attr("d", line);
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
var currentLatLng;
var coordDisplay = document.getElementById('coordinates');

map.on('click', function(e) {
    if (marker) {
        map.removeLayer(marker);
    }
    d3.selectAll(".clim").remove();
    currentLatLng = e.latlng.wrap();
    marker = L.marker(currentLatLng);
    marker.addTo(map);
    coordDisplay.innerHTML = 'Latitude: ' + currentLatLng.lat + ' | Longitude: ' + currentLatLng.lng;
    updateChart(currentLatLng, false);
});

