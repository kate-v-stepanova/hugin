import unittest
import yaml
import os
import shutil

from proper_implementation.flowcells.base_flowcell import BaseFlowcell

DEFAULT_CONFIG = "test_data/config.yaml"

class TestFlowcells(unittest.TestCase):

    def setUp(self):
        """
        Create a fake flowcell. Copy files from test data (test data is present in hugin/tests/test_data dir)
        """
        with open(DEFAULT_CONFIG) as config:
            self.config = (yaml.load(config) or {})
        self.original_data_folder = os.path.join('tests' , self.config.get('data_folders')[0])
        self.fake_data_folder     = os.path.join('test_data')
        self.original_flowcell = os.path.join(self.original_data_folder , '150424_ST-E00214_0031_BH2WY7CCXX')
        self.fake_flowcell     = os.path.join(self.fake_data_folder     , '150424_ST-E00214_0031_BH2WY7CCXX')
        os.mkdir(self.fake_flowcell)

    def test_path(self):
        fc = BaseFlowcell(self.fake_flowcell)
        self.assertEqual(self.fake_flowcell, fc.path)

    def test_run_info_present(self):
        fc = BaseFlowcell(path=self.original_flowcell)
        self.assertIsNotNone(fc.run_info)
        self.assertIsNotNone(fc.run_parameters)
        self.assertIsNotNone(fc.cycle_times)
        self.assertIsNotNone(fc.sample_sheet)




    def tearDown(self):
        shutil.rmtree(self.fake_flowcell, ignore_errors=False)


if __name__ == '__main__':
    unittest.main()