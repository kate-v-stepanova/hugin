import os

from old_hugin.Runs import Run
from hugin.parser import RunInfoParser
from hugin.parser import  HiSeqXSampleSheet


class HiSeqX_Run(Run):
    
    def __init__(self,  path_to_run, samplesheet_folders):
        super(HiSeqX_Run, self).__init__( path_to_run, samplesheet_folders)

    def _sequencer_type(self):
        return "HiSeqX"

    def get_run_info(self):
        """
            Parse the RunInfo.xml file into a dict
        """
        f = os.path.join(self.path,'RunInfo.xml')
        if not os.path.exists(f):
            return {}
        with open(f) as fh:
            rip = RunInfoParser()
            runinfo = rip.parse(fh)
        return runinfo


    def get_projects(self):
        ssheet = self.samplesheet
        if ssheet is None:
            return None
        samplesheet_Obj = HiSeqXSampleSheet(ssheet)
        return samplesheet_Obj.return_projects()



    def get_run_mode(self):
        return "HiSeqX"


    def _get_demux_dir(self):
        if os.path.exists(os.path.join(self.path, "Demultiplexing")):
            return os.path.join(self.path, "Demultiplexing")
        return None

    def _is_demultiplexing_started(self):
        if os.path.exists(os.path.join(self.path, "Demultiplexing")):
            return True
        else:
            return False

    def _is_demultiplexing_done(self):
        if os.path.exists(os.path.join(self.path, 'Demultiplexing', 'Stats', 'DemultiplexingStats.xml')):
            return True
        else:
            return False












