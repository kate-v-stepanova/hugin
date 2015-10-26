import unittest
import os
import yaml
import shutil
import datetime

from better_implementation.flowcells.flowcell import HiseqXFlowcell, FC_STATUSES

CURRENT_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG = os.path.join(CURRENT_DIR, "config.yaml")


class TestHiSeqXFlowcells(unittest.TestCase):

    def setUp(self):
        with open(DEFAULT_CONFIG) as config:
            self.config = (yaml.load(config) or {})

        self.data_folder = os.path.join(CURRENT_DIR, self.config.get('data_folders')[0])
        self.fake_flowcell = os.path.join(self.data_folder, '151021_ST-E00144_0013_FAKE')
        if os.path.exists(self.fake_flowcell):
            shutil.rmtree(self.fake_flowcell)
        os.mkdir(self.fake_flowcell)

    def test_sequencing_started(self):
        fc = HiseqXFlowcell(self.fake_flowcell)
        sequencing_started = datetime.datetime.fromtimestamp(os.path.getctime(self.fake_flowcell))
        self.assertEqual(fc.sequencing_started, sequencing_started)

    def test_sequencing_done(self):
        rta_file = os.path.join(self.data_folder, 'RTAComplete.txt')
        shutil.copy2(rta_file, self.fake_flowcell)

        fc = HiseqXFlowcell(self.fake_flowcell)
        sequencing_done = datetime.datetime.fromtimestamp(os.path.getctime(rta_file))
        self.assertEqual(fc.sequencing_done, sequencing_done)
        os.remove(os.path.join(self.fake_flowcell, 'RTAComplete.txt'))

    def test_duration(self):
        cycle_times = os.path.join(self.data_folder, 'CycleTimes.txt')
        logs_dir = os.path.join(self.fake_flowcell, 'Logs')
        os.mkdir(logs_dir)
        shutil.copy2(cycle_times, logs_dir)

        fc = HiseqXFlowcell(self.fake_flowcell)
        end_time =

        shutil.rmtree(logs_dir)


    # def test_sample_sheet(self):
    #     self.assertTrue(False)


    # def test_status_demultiplexing(self):
    #     filename = os.path.join(self.fake_flowcell, 'Demultiplexing')
    #     os.mkdir(filename)
    #     fc_status = FlowcellStatus(self.fake_flowcell)
    #
    #     self.assertEqual(fc_status.status, FC_STATUSES['DEMULTIPLEXING'])
    #     os.rmdir(filename)
    #
    # def test_due_date(self):
    #     cycle_times_path = os.path.join(self.data_folder, "CycleTimes.txt")
    #     logs_dir = os.path.join(self.fake_flowcell, 'Logs')
    #     os.mkdir(logs_dir)
    #     shutil.copy2(cycle_times_path, logs_dir)
    #
    #     run_info_path = os.path.join(self.data_folder, "RunInfo.xml")
    #     shutil.copy2(run_info_path, self.fake_flowcell)
    #
    #     due_date = datetime.datetime(2015, 8, 28, 3, 0, 51, 405770)
    #
    #     fc_status = FlowcellStatus(self.fake_flowcell)
    #     fc = HiseqXFlowcell(fc_status)
    #     self.assertEqual(due_date, fc.due_time)
    #
    #     os.remove(os.path.join(self.fake_flowcell, 'RunInfo.xml'))
    #     shutil.rmtree(logs_dir)
    #
    # def test_check_status(self):
    #     cycle_times_path = os.path.join(self.data_folder, "CycleTimes.txt")
    #     logs_dir = os.path.join(self.fake_flowcell, 'Logs')
    #     os.mkdir(logs_dir)
    #     shutil.copy2(cycle_times_path, logs_dir)
    #
    #     fc_status = FlowcellStatus(self.fake_flowcell)
    #     fc = HiseqXFlowcell(fc_status)
    #     self.assertTrue(fc.check_status())
    #     shutil.rmtree(logs_dir)


    def tearDown(self):
        shutil.rmtree(self.fake_flowcell, ignore_errors=False)


if __name__ == '__main__':
    unittest.main()