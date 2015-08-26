import argparse
import os

from reportlib.utils import MergeJson
from reportlib.utils import MergeTsv
from reportlib.utils import MergeFastqc


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

    Report = MergeJson(inputs, args.output_fp)
    Report.run()

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

    Report = MergeJson(inputs, args.output_fp)
    Report.run()


def tsv_report(argv=None):
    p=argparse.ArgumentParser()
    
    # input
    p.add_argument("--input-dir", required=True,
                   help="Directory where the sample results are located.")
    p.add_argument("--input-suffix", required=True,
                   help="Input file suffixes")
    
    # output
    p.add_argument("--output-fp", required=True,
                   help="Output report file")
    args=p.parse_args(argv)

    Report = MergeTsv(args.input_dir, args.input_suffix, args.output_fp)
    Report.run()


def fastqc_report(argv=None):
    p=argparse.ArgumentParser()
    
    # input
    p.add_argument("--input-dir", required=True,
                   help="Directory with fastqc results created by illqc (before and after trim)")
    p.add_argument("--before-trim-subfolder-dir", default="before_trim",
                   help="Subdirectory for before trim fastqc results")
    p.add_argument("--after-trim-subfolder-dir", default="after_trim",
                   help="Subdirectory for after trim fastqc results")
    
    # output
    p.add_argument("--output-dir", required=True,
                   help="Output directory where the files will be saved")
    p.add_argument("--output-base", default="fastqc",
                   help="Base name for the fastqc reports")
    args=p.parse_args(argv)

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    
    # generate the reports
    before_report = MargeFastqc(args.input_dir, args.before_trim_subfolder_dir,
                                 args.output_dir, args.output_base)
    before_report.run()
    
    after_report = MergeFastqc(args.input_dir, args.after_trim_subfolder_dir,
                                args.output_dir, args.output_base)
    after_report.run()
