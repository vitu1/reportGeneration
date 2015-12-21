import json
import os
import glob
import pandas
import re
import StringIO

class MergeJson(object):
    def __init__(self, inputs, out_fp):
        self.inputs = inputs
        self.out_fp = out_fp
        
    def run(self):
        "Combines the information from multiple processing steps."

        # get the sample data for each summary type
        report_list = [self._build_table(*input) for input in self.inputs]

        # merge the DataFrames of all summary types 
        reports = pandas.concat(report_list, axis=1)
        reports.to_csv(self.out_fp, sep='\t', index_label='Samples')
        
    def _build_table(self, summary_dir, summary_prefix, headers):
        "Return a dataframe for the requested summary information for a single prefix"
        fps = sorted(glob.glob(os.path.join(summary_dir, summary_prefix + '*')))
        summary_list = [self._parse_results(fp, summary_prefix, headers) for fp in fps]
        return pandas.concat(summary_list)
    
    def _parse_results(self, fp, summary_prefix, headers):
        "Returns a DaraFrame of results for a given file"
        return pandas.DataFrame(self._get_values(fp, headers), index=[self._get_sample_name(fp, summary_prefix)])
        
    def _get_values(self, fp, headers):
        "Obtains the requested information from the data field of the summary file."
        if os.path.isfile(fp):
            with open(fp) as f_in:
                summary = json.load(f_in)
                summary_data = summary.get('data', {})
        else:
            summary_data={}
        return {header:summary_data.get(header, None) for header in headers}

    def _get_sample_name(self, fp, summary_prefix):
        "Gets the sample name from the summary filepath"
        return fp.rsplit(summary_prefix)[1]

class MergeTsv(object):
    def __init__(self, input_dir, input_suffix, output_fp):
        self.input_dir = input_dir
        self.input_suffix = input_suffix
        self.output_fp = output_fp
        
    def run(self):
        "Returns a DataFrame combining the results of all samples."
        fps = sorted(glob.glob(os.path.join(self.input_dir, '*' + self.input_suffix)))

        # filter out the files that don't have any results
        fps = [fp for fp in fps if os.path.getsize(fp)>1]

        # build pandas dataframes for each file of results
        kos = [self._parse_results(fp) for fp in fps]

        # merge the column results
        kos = pandas.concat(kos, axis=1)

        # write them to file. Replace NAs (due to merging) with 0.
        kos.to_csv(self.output_fp, sep='\t', na_rep=0, index_label="Term")

    def _parse_results(self, fp):
        "Returns a DataFrame containing the results of a single sample"
        return pandas.read_csv(fp, sep='\t', index_col=0, names=[self._get_sample_name(fp, self.input_suffix)], skiprows=1)

    def _get_sample_name(self, fp, input_suffix):
        "Parses the sample name out of the results filepath."
        return os.path.basename(fp).rsplit(input_suffix)[0]

class MergeFastqc(object):
    def __init__(self, input_dir, sub_dir, output_dir, output_base):
        self.input_dir = input_dir
        self.sub_dir = sub_dir
        self.output_dir = output_dir
        self.output_base = output_base
        
    def run(self):
        "Generates summary and quality reports for all samples"
        folders = sorted(glob.glob(os.path.join(self.input_dir, self.sub_dir, '*' + '_fastqc')))
        summary_list = []
        quality_list = []
        for folder in folders:
            with open(os.path.join(folder, 'summary.txt')) as f_in:
                summary_list.append(self._parse_fastqc_summary(f_in))
            with open(os.path.join(folder, 'fastqc_data.txt')) as f_in:
                quality_list.append(self._parse_fastqc_quality(f_in))

        summary_table = pandas.concat(summary_list, axis=1)#.transpose()
        summary_table.to_csv(self.build_output_path('summary'), sep='\t')

        quality_table = pandas.concat(quality_list, axis=1).transpose()
        quality_table.to_csv(self.build_output_path('quality'), sep='\t', index_label="Samples")
        
    def _parse_fastqc_quality(self, f_in):
        "Returns a DataFrame containing the average quality results of a single sample"
        report = f_in.read()
        tableString = re.search('\>\>Per base sequence quality.*?\n(.*?)\n\>\>END_MODULE', report, re.DOTALL).group(1)
        f_s = StringIO.StringIO(tableString)
        df = pandas.read_csv(f_s, sep='\t', usecols=['#Base', 'Mean'], index_col='#Base')
        df.columns=[self._get_sample_name(f_in.name)]
        f_s.close()
        return df
                
    def _parse_fastqc_summary(self, f_in):
        "Returns a DataFrame containing the summary results of a single sample"
        return pandas.read_csv(f_in, sep='\t', header=None, usecols=[0,1], index_col='Category',
                               names=[self._get_sample_name(f_in.name), 'Category'])
        
    def _get_sample_name(self, input_fp):
        "Parses the sample name out of the results folderpath."
        return os.path.basename(os.path.dirname(input_fp)).split('_fastqc')[0]
        
    def build_output_path(self, type):
        "Builds an output filepath according to the type of summary (summary, quality etc)"
        return os.path.join(self.output_dir, '_'.join((self.output_base, self.sub_dir, type)) + '.tsv')
