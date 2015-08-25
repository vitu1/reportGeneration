import json
import os
import glob
import pandas
import re
import StringIO

class ReportFromJson(object):
    def __init__(self, inputs, out_fp):
        self.inputs = inputs
        self.out_fp = out_fp
        
    def run(self):
        "Combines the information from multiple processing steps."
        reports = pandas.concat([self._build_table(*input) for input in self.inputs], axis=1)
        reports.to_csv(self.out_fp, sep='\t', index_label='Samples')
        
    def _build_table(self, summary_dir, summary_prefix, headers):
        "Return a dataframe for the requested summary information for a single prefix"
        fps = sorted(glob.glob(os.path.join(summary_dir, summary_prefix + '*')))
        return pandas.concat([pandas.DataFrame(self._get_values(fp, headers), index=[self._get_sample_name(fp, summary_prefix)]) for fp in fps])
    
    def _get_sample_name(self, fp, summary_prefix):
        "Gets the sample name from the summary filepath"
        return fp.rsplit(summary_prefix)[1]

    def _get_values(self, fp, headers):
        "Obtains the requested information from the data filed of the summary file."
        if os.path.isfile(fp):
            with open(fp) as f_in:
                summary = json.load(f_in)
                summary_data = summary.get('data', {})
        else:
            summary_data={}
        return {header:summary_data.get(header, None) for header in headers}

class ReportFromTsv(object):
    def __init__(self, input_dir, input_suffix, output_fp):
        self.input_dir = input_dir
        self.input_suffix = input_suffix
        self.output_fp = output_fp
        
    def run(self):
        "Return a dataframe for the requested summary information"
        fps = sorted(glob.glob(os.path.join(self.input_dir, '*' + self.input_suffix)))
        kos = pandas.concat(
            [pandas.read_csv(fp, sep='\t', index_col=0, names=[self._get_sample_name_tsv(fp, self.input_suffix)], skiprows=1)
             for fp in fps if os.path.getsize(fp)>1], axis=1)
        kos.to_csv(self.output_fp, sep='\t', na_rep=0, index_label="Term")

    def _get_sample_name_tsv(self, fp, input_suffix):
        return os.path.basename(fp).rsplit(input_suffix)[0]

class ReportFastqc(object):
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
        with open(input_fp) as f_in:
            return pandas.read_csv(f_in, sep='\t', header=None, usecols=[0,1], index_col='Category',
                                   names=[self.get_sample_name(input_fp), 'Category'])
        
    def get_sample_name(self, input_fp):
        return os.path.basename(os.path.dirname(input_fp)).split('_fastqc')[0]
        
    def build_output_path(self, type):
        return os.path.join(self.output_dir, '_'.join((self.output_base, self.sub_dir, type)) + '.tsv')
