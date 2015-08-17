import pandas
import os
from subprocess import check_output

worldclim_dir = "/Users/mperry/data/worldclim"
OUTDIR = os.path.join(worldclim_dir, "stacked")

def make_stack(variable, period, month, rcp, paths):
    outpath = os.path.join(OUTDIR,
                           "{}_{}_{}_{}_stack.tif".format(variable, period, month, rcp))
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


# Load dataframe in global scope
df = pandas.read_csv("../climate_data.csv")


def main():
    # import glob
    # for f in glob.glob(OUTDIR + "/*stack.tif"):
    #     os.remove(f)

    # Only precipt, temp variables
    dfs = df[(df['variable'] == 'tx') |
             (df['variable'] == 'tn') |
             (df['variable'] == 'pr')]

    dfg = dfs.groupby(['variable', 'period', 'month', 'rcp'])

    with open("../climate_stacks.csv", 'w') as fh:
        fh.write("variable,period,month,rcp,path\n")
        for i, record in dfg:
            if i[3] == '45':  # ignore rcp 4.5 for now
                continue
            print(i)
            outpath = make_stack(*i, paths=list(record['path']))
            line = ','.join([str(x) for x in i]) + "," + outpath + "\n"
            fh.write(line)
            fh.flush()

if __name__ == "__main__":
    main()
