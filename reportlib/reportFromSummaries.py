import json
import os
import glob
import csv
import argparse
import pandas

def concat_summaries(inputs, out_fp):
    "Combines the information from multiple processing steps."
    reports = pandas.concat([build_table(*input) for input in inputs], axis=1)
    reports.to_csv(out_fp, sep='\t', index_label='Samples')

def build_table(summary_dir, summary_prefix, headers):
    "Return a dataframe for the requested summary information for a single prefix"
    fps = sorted(glob.glob(os.path.join(summary_dir, summary_prefix + '*')))
    return pandas.concat([pandas.DataFrame(get_values(fp, headers), index=[get_sample_name(fp, summary_prefix)]) for fp in fps])

def get_sample_name(fp, summary_prefix):
    "Gets the sample name from the summary filepath"
    return fp.rsplit(summary_prefix)[1]

def get_values(fp, headers):
    "Obtains the requested information from the data filed of the summary file."
    if os.path.isfile(fp):
        with open(fp) as f_in:
            summary = json.load(f_in)
            summary_data = summary.get('data', {})
            print(summary_data)
    else:
        summary_data={}
    return {header:summary_data.get(header, None) for header in headers}

def preprocess_report(argv=None):
    p=argparse.ArgumentParser()

    # input
    p.add_argument("--illqc-dir", required=True,
                   help="Directory for illqc summary files")
    p.add_argument("--decontam-dir", required=True,
                   help="Direcrory for decontamination summary files")
    p.add_argument("--illqc-prefix", default="summary-illqc_",
                   help="Prefix of the illqc summary files")
    p.add_argument("--decontam-prefix", default="summary-decontam_",
                   help="Prefix of the decontam summary files")

    # output
    p.add_argument("--output-fp", required=True,
                   help="Output report file")
    args=p.parse_args(argv)

    inputs = [
        (args.illqc_dir, args.illqc_prefix, ["input", "both kept", "rev only", "dropped", "fwd only"]),
        (args.decontam_dir, args.decontam_prefix, ["true", "false"])
        ]
    
    concat_summaries(inputs, args.output_fp)

def ko_assignment_report(argv=None):

    p=argparse.ArgumentParser()
    
    # input
    p.add_argument("--pathway-dir", required=True,
                   help="Directory for pathfinder summary files")
    p.add_argument("--decontam-dir", required=True,
                   help="Direcrory for decontamination summary files")
    p.add_argument("--pathway-prefix", default="summary-pathway_",
                   help="Prefix of the pathfinder summary files")
    p.add_argument("--decontam-prefix", default="summary-decontam_",
                   help="Prefix of the decontam summary files")
    
    # output
    p.add_argument("--output-fp", required=True,
                   help="Output report file")
    args=p.parse_args(argv)
    
    inputs = [
        (args.decontam_dir, args.decontam_prefix, ["true"]),
        (args.pathway_dir, args.pathway_prefix, ["ko_hits", "mapped_sequences", "unique_prot_hits", "unique_ko_hits", "mapped_sequences_evalue"])
        ]
    
    concat_summaries(inputs, args.output_fp)
