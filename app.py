import pandas
import math
from rasterstats import zonal_stats
from statistics import median  # python 3.4 only

from flask import Flask, jsonify, request
app = Flask(__name__)


def query_clim(df, rcp, lat, lng, variable="tx", period="70", units="C"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
    medians = []
    maxes = []
    wkt = 'POINT({} {})'.format(lng, lat)
    for month in [x+1 for x in range(12)]:
        monthsub = sub[df['month'] == month]
        vals = []
        # Loop through paths and run zonal stats against each
        for path in monthsub['path']:
            val = zonal_stats(wkt, path, stats="mean")[0]['mean']
            if math.isnan(val):
                raise ValueError("No data for {} at this location".format(path))
            if variable in ('tx', 'tn'):
                # Temp are mult by 10x C, divided by 10 to get C
                val = val / 10.0
                # Then convert to Fahrenheit if specified
                if units == "F":
                    val = ((val / 5.0) * 9) + 32

            vals.append(val)

        # find min, max for this month
        mins.append(min(vals))
        maxes.append(max(vals))
        medians.append(median(vals))

    data = {
        "period": period,
        "min": min(mins),
        "max": max(maxes),
        "data": [{'month': i+1, 'min': x[0], 'median': x[1], 'max': x[2]}
                 for i, x in enumerate(zip(mins, medians, maxes))]}

    return data


# Load dataframe in global scope
df = pandas.read_csv("climate_data.csv")


@app.route("/api/<variable>/<period>")
def api(variable, period):
    kwargs = dict(
        lat=request.args.get('lat'),
        lng=request.args.get('lng'),
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
