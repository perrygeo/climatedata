import pandas
import os
import rasterio
from statistics import median  # python 3.4 only
from subprocess import check_output


def tiny_window(dataset, x, y):
    r, c = dataset.index(x, y)
    return ((r, r+1), (c, c+1))


def make_stack(paths, variable, period, month, rcp):
    outpath = "/tmp/{}_{}_{}_{}_stack.tif".format(variable, period, month, rcp)
    if not os.path.exists(outpath):
        vargs = ["rio", "stack",
                 "--co", "COMPRESS=DEFLATE",
                 "--co", "PREDICTOR=2", "--co", "ZLEVEL=6",
                 "--co", "TILED=YES",
                 "--co", "BLOCKXSIZE=16", "--co", "BLOCKYSIZE=16",
                 "-o", outpath]
        vargs.extend(paths)
        check_output(vargs)
    return outpath


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
                           variable, period, month, rcp)
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
    import glob
    for f in glob.glob("/tmp/*stack.tif"):
        os.remove(f)

    print("Warming up by creating tiffs...")
    query_clim4(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")

    print("Timing....")
    import timeit
    cmd4 = 'query_clim4(df, lat=12.05, lng=-61.75, units="C", period="70", variable="tx", rcp="85")'
    print(timeit.timeit(cmd4, number=50, setup="from __main__ import df, query_clim4"))


if __name__ == "__main__":
    main()
