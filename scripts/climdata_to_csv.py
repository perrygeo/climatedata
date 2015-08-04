"""
A directory of climate data -> a json describing it

keys:
    rcp
    period
    model
    variable
    filepath
    month
    units
"""
import os
import pandas
from glob import glob
from rasterstats import zonal_stats
from itertools import chain

worldclim_dir = "/Users/mperry/data/worldclim"

def past_rasts():
    past_dir = os.path.join(worldclim_dir, 'past')
    for prast in glob(past_dir + "/*.tif"):
        base = os.path.basename(prast)
        name, _ = os.path.splitext(base)
        model = name[0:2]
        period = name[2:5]
        var = name[5:7]
        if var != 'bi':
            month = int(name[7:])
        else:
            month = 0
            var = var + name[7:]
        data = {
            'rcp': 'na',
            'period': period,
            'model': model,
            'month': month,
            'variable': var,
            'path': prast
        }
        yield data


def future_rasts():
    future_dir = os.path.join(worldclim_dir, 'future')
    for rast in glob(future_dir + "/*.tif"):
        base = os.path.basename(rast)
        name, _ = os.path.splitext(base)

        model = name[0:2]
        rcp = name[2:4]
        var = name[4:6]
        period = name[6:8]
        if var != 'bi':
            month = int(name[8:])
        else:
            month = 0
            var = var + name[8:]

        data = {
            'rcp': rcp,
            'period': period,
            'model': model,
            'month': month,
            'variable': var,
            'path': rast
        }
        yield data


def current_rasts():
    current_dir = os.path.join(worldclim_dir, 'current')
    # ESRI Grids, not geotiffs
    variables = {
        'tmax': 'tx',
        'tmin': 'tn',
        'prec': 'pr',
        'bio': 'bi',
    }
    for customvar, var in variables.items():
        path_tmp = os.path.join(current_dir, customvar, customvar + "_*")
        for rast in glob(path_tmp):
            num = os.path.basename(rast).split("_")[1]
            if var != 'bi':
                month = int(num)
            else:
                month = 0
                var = var + num

            data = {
                'rcp': 'na',
                'period': 'current',
                'model': 'na',
                'month': month,
                'variable': var,
                'path': rast + "/hdf.adf"
            }
            yield data


def get_dataframe():
    all_data = chain(past_rasts(), future_rasts(), current_rasts())
    return pandas.DataFrame(list(all_data))




if __name__ == "__main__":
    df = get_dataframe()
    df.to_csv("climate_data.csv", index=False)

    # df = pandas.read_csv("climate_data.csv")
    # import ipdb; ipdb.set_trace()
