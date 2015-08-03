import json
import os
import glob
import csv
import argparse
from pandas import *

def makeReport(summary_dir, output_fp, prefix):
    """
    Compiles the summary files for individual samples into one tsv file
    :param summary_dir: path to the directory where all the summary json files are located
    :param prefix: the prefix of the summary files to pick
    :param output_fp: filepath of the output
    """
    summaries=[]
    for file in glob.glob(os.path.join(summary_dir, prefix + '*')):
        sample = file.rsplit(prefix)[1]
        with open(file) as f_in:
            summary_data = json.load(f_in).get('data', {})
        summaries.append(DataFrame(summary_data, index=[sample]))

    # outer merge all the samples
    all = concat(summaries)

    # sort the columns to have numeric order
    cols = all.columns.tolist()
    sortedTable = all[sorted(cols, key=lambda k: float(k.rsplit('-')[0]))] #.tanspose()

    # write to tsv
    sortedTable.to_csv(output_fp, sep='\t')


def main(argv=None):
    p=argparse.ArgumentParser()

    # input
    p.add_argument("--summary-dir", required=True,
                   help="Directory for fastqc summary files")
    p.add_argument("--summary-prefix", default="summary-fastqcBefore_",
                   help="Prefix of the fastqc summary files")

    # output
    p.add_argument("--output-fp", required=True,
                   help="Output report file")
    args=p.parse_args(argv)
    
    makeReport(args.summary_dir, args.output_fp, args.summary_prefix)
