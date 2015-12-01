import os
import tempfile
import unittest

class PathfinderTest(unittest.TestCase):
    def setUp(self):
        self.config = get_config(None) # get user specific config
        self.output_dir = tempfile.mkdtemp()
        self.summary_fp = os.path.join(self.output_dir, "summary.txt")
        
    def tearDown(self):
        shutil.rmtree(self.output_dir)
