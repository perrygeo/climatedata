import pandas
import rasterio
import os
from statistics import median  # python 3.4 only

from flask import Flask, jsonify, request
app = Flask(__name__)

stacked_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacks")

# Load dataframe in global scope
df = pandas.read_csv("climate_stacks.csv")


def tiny_window(dataset, x, y):
    r, c = dataset.index(x, y)
    return ((r, r+1), (c, c+1))


def query_clim(df, rcp, lat, lng, variable="tx", period="70", units="C"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
    medians = []
    maxes = []

    for month in [x+1 for x in range(12)]:
        monthsub = sub[sub['month'] == month]
        path = monthsub['path'].tolist()[0]
        stackpath = os.path.join(stacked_dir, path)

        # Loop through paths and run zonal stats against each
        with rasterio.open(stackpath) as src:
            win = tiny_window(src, lng, lat)
            arr = src.read(window=win)

        vals = arr[:, 0, 0]
        # TODO check null
        # if math.isnan(val):
        #     raise ValueError("No data for {} at this location".format(path))

        if variable in ('tx', 'tn'):
            # Temp are mult by 10x C, divided by 10 to get C
            vals = vals / 10.0
            # Then convert to Fahrenheit if specified
            if units == "F":
                vals = ((vals / 5.0) * 9) + 32

        # find min, max for this month
        mins.append(float(min(vals)))
        maxes.append(float(max(vals)))
        medians.append(float(median(vals)))

    data = {
        "period": period,
        "min": min(mins),
        "max": max(maxes),
        "data": [{'month': i+1, 'min': x[0], 'median': x[1], 'max': x[2]}
                 for i, x in enumerate(zip(mins, medians, maxes))]}

    return data


@app.route('/')
def root():
    return app.send_static_file("index.html")

@app.after_request
def add_header(response):
    response.cache_control.max_age = 36000
    return response

@app.route("/api/<variable>/<period>")
def api(variable, period):
    kwargs = dict(
        lat=float(request.args.get('lat')),
        lng=float(request.args.get('lng')),
        units=request.args.get('units'),
        period=period,
        variable=variable,
        rcp=request.args.get('rcp') if 'rcp' in request.args else 'na')

    timestamp = request.args.get('timestamp', default=0.0, type=float)

    data = query_clim(df, **kwargs)
    data['timestamp'] = timestamp
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
