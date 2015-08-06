import pandas
from rasterstats import zonal_stats


def query_clim(df, rcp, lat, lng, variable="tx", period="70"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
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

    # months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    # from collections import OrderedDict
    # return OrderedDict(zip(months, zip(mins, maxes)))

    return [{'month': i+1, 'min': x[0], 'max': x[1]}
            for i, x in enumerate(zip(mins, maxes))]


# Load dataframe in global scope
df = pandas.read_csv("climate_data.csv")


if __name__ == "__main__":
    lat = 21.94
    lng = 11.25
    data = [
        {"period": "mid", "data": query_clim(df, lat=lat, lng=lng, rcp='na', period='mid')},
        {"period": "lgm", "data": query_clim(df, lat=lat, lng=lng, rcp='na', period='lgm')},
        {"period": "cur", "data": query_clim(df, lat=lat, lng=lng, rcp='na', period='current')},
        {"period": "y50-26", "data": query_clim(df, lat=lat, lng=lng, rcp='26', period='50')},
        {"period": "y70-26", "data": query_clim(df, lat=lat, lng=lng, rcp='26', period='70')},
        {"period": "y50-85", "data": query_clim(df, lat=lat, lng=lng, rcp='85', period='50')},
        {"period": "y70-85", "data": query_clim(df, lat=lat, lng=lng, rcp='85', period='70')}
    ]
