import pandas
import math
import os
import rasterio
from rasterstats import zonal_stats
from statistics import median  # python 3.4 only
from subprocess import check_output

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


def tiny_window(dataset, x, y):
    r, c = dataset.index(x, y)
    return ((r, r+1), (c, c+1))


def make_vrt(paths, variable, rcp, period, month):
    vrtpath = "/tmp/{}_{}_{}_{}.vrt".format(variable, rcp, period, month)
    if not os.path.exists(vrtpath):
        vargs = ["gdalbuildvrt", "-separate", vrtpath]
        vargs.extend(paths)
        check_output(vargs)
    return vrtpath


def make_stack(paths, variable, rcp, period, month):
    outpath = "/tmp/{}_{}_{}_{}_stack.tif".format(variable, rcp, period, month)
    if not os.path.exists(outpath):
        vargs = ["rio", "stack", "-o", outpath]
        vargs.extend(paths)
        check_output(vargs)
    return outpath


def query_clim2(df, rcp, lat, lng, variable="tx", period="70", units="C"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
    medians = []
    maxes = []
    for month in [x+1 for x in range(12)]:
        monthsub = sub[df['month'] == month]
        vals = []
        # Loop through paths and run zonal stats against each
        for path in monthsub['path']:
            with rasterio.open(path) as src:
                win = tiny_window(src, lng, lat)
                arr = src.read(window=win)

            val = arr[0][0][0]
            # val = zonal_stats(wkt, path, stats="mean")[0]['mean']
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


def query_clim3(df, rcp, lat, lng, variable="tx", period="70", units="C"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
    medians = []
    maxes = []
    for month in [x+1 for x in range(12)]:
        monthsub = sub[df['month'] == month]
        # Loop through paths and run zonal stats against each
        vrt = make_vrt([path for path in monthsub['path']],
                       variable, rcp, period, month)
        with rasterio.open(vrt) as src:
            win = tiny_window(src, lng, lat)
            arr = src.read(window=win)

        vals = arr[:, 0, 0]

        # TODO null checks
        # if math.isnan(val):
        #     raise ValueError("No data for {} at this location".format(path))

        if variable in ('tx', 'tn'):
            # Temp are mult by 10x C, divided by 10 to get C
            vals = vals / 10.0
            # Then convert to Fahrenheit if specified
            if units == "F":
                vals = ((vals / 5.0) * 9) + 32

        # find min, max for this month
        mins.append(vals.min())
        maxes.append(vals.max())
        medians.append(median(vals))

    data = {
        "period": period,
        "min": min(mins),
        "max": max(maxes),
        "data": [{'month': i+1, 'min': x[0], 'median': x[1], 'max': x[2]}
                 for i, x in enumerate(zip(mins, medians, maxes))]}

    return data


def query_clim4(df, rcp, lat, lng, variable="tx", period="70", units="C"):
    sub = df[(df['variable'] == variable) &
             (df['rcp'] == rcp) &
             (df['period'] == period)]

    mins = []
    medians = []
    maxes = []
    for month in [x+1 for x in range(12)]:
        monthsub = sub[df['month'] == month]
        # Loop through paths and run zonal stats against each
        stack = make_stack([path for path in monthsub['path']],
                           variable, rcp, period, month)
        with rasterio.open(stack) as src:
            win = tiny_window(src, lng, lat)
            arr = src.read(window=win)

        vals = arr[:, 0, 0]

        # TODO null checks
        # if math.isnan(val):
        #     raise ValueError("No data for {} at this location".format(path))

        if variable in ('tx', 'tn'):
            # Temp are mult by 10x C, divided by 10 to get C
            vals = vals / 10.0
            # Then convert to Fahrenheit if specified
            if units == "F":
                vals = ((vals / 5.0) * 9) + 32

        # find min, max for this month
        mins.append(vals.min())
        maxes.append(vals.max())
        medians.append(median(vals))

    data = {
        "period": period,
        "min": min(mins),
        "max": max(maxes),
        "data": [{'month': i+1, 'min': x[0], 'median': x[1], 'max': x[2]}
                 for i, x in enumerate(zip(mins, medians, maxes))]}

    return data


# Load dataframe in global scope
df = pandas.read_csv("../climate_data.csv")


def main():
    import timeit

    method1 = query_clim(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")
    method2 = query_clim2(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")
    method3 = query_clim3(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")
    method4 = query_clim4(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")
    assert method1 == method2 == method3 == method4

    cmd = 'query_clim(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")'
    print(timeit.timeit(cmd, number=3, setup="from __main__ import df, query_clim"))

    cmd2 = 'query_clim2(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")'
    print(timeit.timeit(cmd2, number=3, setup="from __main__ import df, query_clim2"))

    cmd3 = 'query_clim3(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")'
    print(timeit.timeit(cmd3, number=3, setup="from __main__ import df, query_clim3"))

    cmd4 = 'query_clim4(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")'
    print(timeit.timeit(cmd4, number=3, setup="from __main__ import df, query_clim4"))


if __name__ == "__main__":
    main()
