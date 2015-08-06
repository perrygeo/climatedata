import pandas
from rasterstats import zonal_stats
from statistics import median  # python 3.4 only

from flask import Flask, jsonify, request
app = Flask(__name__)


def query_clim(df, rcp, lat, lng, variable="tx", period="70"):
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
            if variable in ('tx', 'tn'):
                val = val / 10.0  # Temp are mult by 10x C, divided by 10 to get C
            vals.append(val)

        # find min, max for this month
        mins.append(min(vals))
        maxes.append(max(vals))
        medians.append(median(vals))

    # months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    # from collections import OrderedDict
    # return OrderedDict(zip(months, zip(mins, maxes)))

    return [{'month': i+1, 'min': x[0], 'median': x[1], 'max': x[2]}
            for i, x in enumerate(zip(mins, medians, maxes))]


# Load dataframe in global scope
df = pandas.read_csv("climate_data.csv")


@app.route("/api/<period>")
def api(period):
    kwargs = dict(
        lat=request.args.get('lat'),
        lng=request.args.get('lng'),
        period=period,
        rcp=request.args.get('rcp') if 'rcp' in request.args else 'na')

    data = {"period": period,
            "data": query_clim(df, **kwargs)}

    return jsonify(results=data)

if __name__ == "__main__":
    app.run(debug=True)
