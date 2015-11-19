import unittest
import os
import yaml
import shutil
import datetime

from hugin.flowcell_status import FlowcellStatus, FC_STATUSES
from hugin.flowcells.hiseqx import HiSeqXBaseFlowcell
from hugin.flowcells.base_flowcell import BaseFlowcell

DEFAULT_CONFIG = "test_data/config.yaml"


class TestHiSeqXFlowcells(unittest.TestCase):

    def setUp(self):
        with open(DEFAULT_CONFIG) as config:
            self.config = (yaml.load(config) or {})

        self.data_folder = os.path.join('tests', self.config.get('data_folders')[0])
        self.fake_flowcell = os.path.join(self.data_folder, '151021_ST-E00144_0013_FAKE')
        if os.path.exists(self.fake_flowcell):
            shutil.rmtree(self.fake_flowcell)
        os.mkdir(self.fake_flowcell)

    # def test_status_sequencing(self):
    #     fc_status = FlowcellStatus(self.data_folder)
    #     self.assertEqual(fc_status.status, FC_STATUSES['SEQUENCING'])
    #
    # def test_check_status(self):
    #     cycle_times_path = os.path.join(self.data_folder, "CycleTimes.txt")
    #     logs_dir = os.path.join(self.fake_flowcell, 'Logs')
    #     os.mkdir(logs_dir)
    #     shutil.copy2(cycle_times_path, logs_dir)
    #
    #     fc_status = FlowcellStatus(self.fake_flowcell)
    #     fc = HiSeqXFlowcell(fc_status)
    #     self.assertTrue(fc.check_status())
    #     shutil.rmtree(logs_dir)

    def test_class_name(self):
        run_parameters = os.path.join('tests/test_data/150424_ST-E00214_0031_BH2WY7CCXX', 'runParameters.xml')
        shutil.copy2(run_parameters, self.fake_flowcell)

        fc_status = FlowcellStatus(self.fake_flowcell)
        fc = BaseFlowcell.init_flowcell(fc_status)
        self.assertEqual(HiSeqXBaseFlowcell, fc.__class__)


    def tearDown(self):
        shutil.rmtree(self.fake_flowcell, ignore_errors=False)


if __name__ == '__main__':
    unittest.main()