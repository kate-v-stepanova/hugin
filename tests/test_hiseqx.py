import unittest
import yaml
import os
import shutil
import datetime

from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell, FC_STATUSES
from monitor_flowcells.flowcells.hiseqx import HiseqxFlowcell

DEFAULT_CONFIG = "test_data/config.yaml"

class TestFlowcells(unittest.TestCase):

    def setUp(self):
        """
        Create a fake flowcell. Copy files from test data (test data is present in hugin/tests/test_data dir)
        """
        with open(DEFAULT_CONFIG) as config:
            self.config = (yaml.load(config) or {})
        self.original_data_folder = os.path.join('tests' , self.config.get('data_folders')[0])
        self.fake_data_folder     = os.path.join('tests', 'test_data')
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

    def test_seq_demux_started_done(self):
        fc = BaseFlowcell(self.original_flowcell)
        self.assertIsNotNone(fc.sequencing_started)
        # self.assertEqual(type(fc.sequencing_started), type(datetime.datetime))
        self.assertIsNotNone(fc.sequencing_done)
        # self.assertEqual(type(fc.sequencing_done), type(datetime.datetime))
        self.assertIsNotNone(fc.demultiplexing_started)
        # self.assertEqual(type(fc.demultiplexing_started), type(datetime))
        self.assertIsNotNone(fc.demultiplexing_done)
        self.assertSetEqual(set([type(datetime.datetime.now())]), set([type(fc.sequencing_started),
                                                              type(fc.sequencing_done),
                                                              type(fc.demultiplexing_started),
                                                              type(fc.demultiplexing_done)]))


    def test_transferring(self):
        fc = BaseFlowcell(self.original_flowcell)
        self.assertIsNotNone(fc.transfering_started)
        self.assertIsNotNone(fc.transfering_done)


    def test_init_flowcell(self):
        fc = BaseFlowcell.init_flowcell(self.original_flowcell)
        self.assertIsInstance(fc, HiseqxFlowcell)

    def test_sequencing_started(self):
        fc = BaseFlowcell.init_flowcell(self.original_flowcell)
        self.assertIsNotNone(fc.sequencing_started)

    def test_due_date(self):
        fc = BaseFlowcell.init_flowcell(self.original_flowcell)
        self.assertGreater(datetime.datetime.now(), fc.due_date)

    def test_check_status(self):
        fc = BaseFlowcell.init_flowcell(self.original_flowcell)
        self.assertEqual(fc.status, FC_STATUSES['CHECKSTATUS'])
        self.assertIsNotNone(fc.check_status)

    def tearDown(self):
        shutil.rmtree(self.fake_flowcell, ignore_errors=False)


if __name__ == '__main__':
    unittest.main()

def run_test():
    unittest.main()