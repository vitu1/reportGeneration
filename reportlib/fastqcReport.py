import json
import os
import glob
import csv
import argparse
import pandas
import re
import StringIO

class FastqcReport(object):
    def __init__(self, input_dir, sub_dir, output_dir, output_base):
        self.input_dir = input_dir
        self.sub_dir = sub_dir
        self.output_dir = output_dir
        self.output_base = output_base

    def run(self):
        folders = sorted(glob.glob(os.path.join(self.input_dir, self.sub_dir, '*' + '_fastqc')))

        summary_table = pandas.concat([self.parse_fastqc_summary(os.path.join(folder, 'summary.txt')) for folder in folders], axis=1).transpose()
        summary_table.to_csv(self.build_output_path('summary'), sep='\t')

        quality_table = pandas.concat([self.parse_fastqc_quality(os.path.join(folder, 'fastqc_data.txt')) for folder in folders], axis=1).transpose()
        quality_table.to_csv(self.build_output_path('quality'), sep='\t')

    def parse_fastqc_quality(self, input_fp):
        "Parses a summary fastqc file and returns a dataframe with the mean quality per base information for a sample"
        with open(input_fp) as f_in:
            report = f_in.read()
        tableString = re.search('\>\>Per base sequence quality.*?\n(.*?)\n\>\>END_MODULE', report, re.DOTALL).group(1)
        try:
            f_s = StringIO.StringIO(tableString)
            df = pandas.read_csv(f_s, sep='\t', usecols=['#Base', 'Mean'], index_col='#Base')
            df.columns=[self.get_sample_name(input_fp)]
            return df
        finally:
            f_s.close()

    def parse_fastqc_summary(self, input_fp):
        "Parses a summary fastqc file and returns a dataframe with the verdicts of fastqc tests for a sample"
        with open(input_fp) as f_in:
            return pandas.read_csv(f_in, sep='\t', header=None, usecols=[0,1], index_col='Category',
                                   names=[self.get_sample_name(input_fp), 'Category'])

    def get_sample_name(self, input_fp):
        "Obtains the sample name from the folder path"
        return os.path.basename(os.path.dirname(input_fp)).split('_fastqc')[0]

    def build_out_path(self, type):
        "Builds the output filepath for a given summary"
        return os.path.join(self.output_dir, '_'.join((self.output_base, self.sub_dir, type)) + '.tsv')
        
def main(argv=None):
    p=argparse.ArgumentParser()

    # input
    p.add_argument("--input-dir", required=True,
                   help="Main directory with fastqc results created by illqc")
    p.add_argument("--before-trim-subfolder-dir", default="before_trim",
                   help="Subdirectory within input-dir containing before trim fastqc results")
    p.add_argument("--after-trim-subfolder-dir", default="after_trim",
                   help="Subdirectory within input-dir containing after trim fastqc results")

    # output
    p.add_argument("--output-dir", required=True,
                   help="Output directory where the files will be saved")
    p.add_argument("--output-base", default="fastqc",
                   help="Base name for the fastqc reports")
    args=p.parse_args(argv)

    # generate the reports
    before_report = FastqcReport(args.input_dir, args.before_trim_subfolder_dir,
                                 args.output_dir, args.output_base)
    before_report.run()

    after_report = FastqcReport(args.input_dir, args.after_trim_subfolder_dir,
                                 args.output_dir, args.output_base)
    after_report.run()
