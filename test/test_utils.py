
import unittest
import tempfile
import shutil
import pandas

from reportlib.utils import *

class TestJson(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def check_result(self, observed_fp, expected_fp):
        observed = observed_fp.read()
        print(observed)
        with open(expected_fp) as f_in:
            expected = f_in.read()
        self.assertEqual(observed, expected)

    def test_merge_json(self):
        inputs = [
        (self.data_dir, 'summary-illqc_', ["input", "both_kept", "dropped"]),
        (self.data_dir, 'summary-decontam_', ["true", "false"])
        ]
        observed_fp = tempfile.NamedTemporaryFile()
        Report = MergeJson(inputs, observed_fp.name)
        Report.run()

        self.check_result(observed_fp, os.path.join(self.data_dir, 'mergeJson_results.tsv'))

    def test_merge_tsv(self):
        observed_fp = tempfile.NamedTemporaryFile()
        Report = MergeTsv(self.data_dir, '.txt', observed_fp.name)
        Report.run()
        self.check_result(observed_fp, os.path.join(self.data_dir, 'mergeTsv_results.tsv'))

    def test_fastqc_report(self):
        Report = MergeFastqc(self.data_dir, "", self.output_dir, "fastqc")
        Report.run()
        
        summary_observed_fp = Report.build_output_path('summary')
        with open(summary_observed_fp) as f_in:
            self.check_result(f_in, os.path.join(self.data_dir, 'fastqc_summary_results.tsv'))
        
        quality_observed_fp = Report.build_output_path('quality')
        with open(quality_observed_fp) as f_in:
            self.check_result(f_in, os.path.join(self.data_dir, 'fastqc_quality_results.tsv'))

    def test_build_path_fastqc(self):
        Report = MergeFastqc("home/someuser", "before_trim", "home/output_dir", "fastqc")
        observed = Report.build_output_path('summary')
        self.assertEqual(observed, "home/output_dir/fastqc_before_trim_summary.tsv")


#if __name__ == "__main__":
#    unittest.main()
