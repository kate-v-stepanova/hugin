import unittest
import yaml
import os
import shutil
import datetime

from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell, FC_STATUSES
from monitor_flowcells.flowcells.hiseq import HiseqFlowcell
from monitor_flowcells.flowcell_monitor import FlowcellMonitor

from flowcell_parser.classes import SampleSheetParser

# DEFAULT_CONFIG = "tests/config.yaml"

from utils.config.config import CONFIG as config

class TestHiseq(unittest.TestCase):

    def setUp(self):
        self.config = config
        self.nosync_folder = 'tests/test_data/hiseq/nosync'
        for data_folder in self.config['data_folders']:
            if 'hiseq' in data_folder:
                self.data_folder = data_folder
                listdir = os.listdir(self.data_folder)
                for fc in listdir:
                    if 'nosync' not in listdir:
                        self.original_flowcell = os.path.join(self.data_folder, fc)
                        break
        try:
            os.mkdir(self.nosync_folder)
        except Exception as e: pass
        try:
            self.nosync_flowcell = os.path.join(self.nosync_folder, '151111_A00123_0000_FAKE') # just random name
            os.mkdir(self.nosync_flowcell)
        except Exception as e: pass #raise e
        try:
            shutil.copyfile(os.path.join(self.original_flowcell, 'runParameters.xml'), os.path.join(self.nosync_flowcell, 'runParameters.xml'))
        except Exception as e: raise e


    def test_flowcell_monitor(self):
        monitor = FlowcellMonitor(self.config)
        data_folders = monitor.data_folders
        self.assertEqual(data_folders, config.get('data_folders'))

    def test_nosync(self):
        monitor = FlowcellMonitor(self.config)
        nosync_flowcells = monitor.get_nosync_flowcells()
        nosync_flowcell = HiseqFlowcell(self.nosync_flowcell)
        self.assertEqual(nosync_flowcells, [nosync_flowcell])


    def test_init_flowcell(self):
        fc = BaseFlowcell.init_flowcell(self.original_flowcell)
        self.assertIsInstance(fc, HiseqFlowcell)

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
        shutil.rmtree(self.nosync_folder)


if __name__ == '__main__':
    unittest.main()
