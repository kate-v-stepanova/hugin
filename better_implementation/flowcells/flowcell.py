import socket
import datetime
import os

from flowcell_parser.classes import RunParametersParser

from better_implementation.parsers.run_info import RunInfo
from better_implementation.parsers.run_parameters import RunParameters
from better_implementation.parsers.sample_sheet import SampleSheet
from better_implementation.parsers.cycle_times import CycleTimes

# flowcell statuses
FC_STATUSES =  {
	'ABORTED'       : "Aborted",         # something went wrong in the FC
	'CHECKSTATUS'   : "Check status",    # demultiplex failure
	'SEQUENCING'    : "Sequencing",      # under sequencing
	'DEMULTIPLEXING': "Demultiplexing",  # under demultiplexing
	'TRANFERRING'   : "Transferring",    # tranferring to HPC resource
	'NOSYNC'        : "Nosync",          # in nosync folder
	'ARCHIVED'      : 'Archived',        # removed from nosync folder
}

CYCLE_DURATION = {
	'RapidRun'          : datetime.timedelta(minutes=12),
	'HighOutput'        : datetime.timedelta(minutes=100),
	'RapidHighOutput'   : datetime.timedelta(minutes=43),
	'MiSeq'             : datetime.timedelta(minutes=6),
	'HiSeqX'            : datetime.timedelta(minutes=10),
}

DURATIONS = {
	'DEMULTIPLEXING'    : datetime.timedelta(hours=4),
	'TRANSFERING'       : datetime.timedelta(hours=12)
}

class Flowcell(object):
    def __init__(self, flowcell_dir):
        self._path = flowcell_dir
        self._run_info = None
        self._run_paramters = None
        self._sample_sheet = None
        self._cycle_times = None

        self._status = None
        self._check_status = None
        self._warning = None

        self._sequencing_started = None
        self._sequencing_end_time = None
        self._sequencing_done = None
        self._demultiplexing_started = None
        self._demultiplexing_end_time = None
        self._demultiplexing_done = None
        self._transfering_started = None
        self._transfering_end_time = None
        self._transfering_done = None

    @property
    def path(self):
        return self._path

    @property
    def cycle_times(self):
        if self._cycle_times is None:
            self._cycle_times = CycleTimes(self.path)
        return self._cycle_times

    @property
    def run_info(self):
        if self._run_info is None:
            self._run_info = RunInfo(self.path)
        return self._run_info

    @property
    def run_parameters(self):
        if self._run_paramters is None:
            self._run_parameters = RunParameters(self.path)
        return self._run_paramters

    @property
    def sample_sheet(self):
        if self._sample_sheet is None:
            self._sample_sheet = SampleSheet(self.path)
        return self._sample_sheet

    @property
    def status(self):
        if self._status is None:
            # todo: define status
            pass
        return self._status if not self.check_status else FC_STATUSES['CHECKSTATUS']

    @property
    def check_status(self):
        if not self._check_status:
            pass
            # todo: implement check_status
        return self._check_status


    @classmethod
    def init_flowcell(cls, flowcell_dir):
        try:
            parser = RunParametersParser(os.path.join(flowcell_dir, 'runParameters.xml'))
            # print rp.data

        except OSError:
            raise RuntimeError("Cannot find the runParameters.xml file at {}. This is quite unexpected.".format(flowcell_dir))
        else:
            try:
                runtype = parser.data['RunParameters']["Setup"]["Flowcell"]
            except KeyError:
                # logger.warn("Parsing runParameters to fecth instrument type, not found Flowcell information in it. Using ApplicaiotnName")
                runtype = parser.data['RunParameters']['Setup'].get("ApplicationName", '')

            # depending on the type of flowcell, return instance of related class
            if "HiSeq X" in runtype:
                return HiseqXFlowcell(flowcell_dir)
            elif "MiSeq" in runtype:
                return MiSeqFlowcell(flowcell_dir)
            elif "HiSeq" in runtype or "TruSeq" in runtype:
                return HiSeqFlowcell(flowcell_dir)
            else:
                raise RuntimeError("Unrecognized runtype {} of run {}. Someone as likely bought a new sequencer without telling it to the bioinfo team".format(runtype, flowcell_dir))


class HiseqXFlowcell(Flowcell):
    def __init__(self, status):
        super(HiseqXFlowcell, self).__init__(status)

    @property
    def full_name(self):
        return os.path.basename(self.path)

    @property
    def name(self):
        # todo: returns the wrong name
        return self.run_info['Flowcell']

    @property
    def chemistry(self):
        return self.run_parameters['ChemistryVersion']

    def check_status(self):
        if self.status == FC_STATUSES['SEQUENCING']:
            return self._check_sequencing()
        elif self.status == FC_STATUSES['DEMULTIPLEXING']:
            return self._check_demultiplexing()
        elif self.status == FC_STATUSES['TRANFERRING']:
            return self._check_transferring()

    @property
    def sequencing_started(self):
        if self._sequencing_started is None:
            self._sequencing_started = datetime.datetime.fromtimestamp(os.path.getctime(self.path))
        return self._sequencing_started

    @property
    def sequencing_done(self):
        if self._sequencing_done is None:
            # if RTAComplete.txt is present, sequencing is done
            rta_file = os.path.join(self.path, 'RTAComplete.txt')
            if os.path.exists(rta_file):
                self._sequencing_done = datetime.datetime.fromtimestamp(os.path.getmtime(rta_file))
        return self._sequencing_done

    @property
    def sequencing_end_time(self):
        if not self._sequencing_end_time:
            start_time = self.sequencing_started
            run_mode = self.sample_sheet.run_mode
            cycle_duration = self.cycle_times.average_cycle_time if self.cycle_times else CYCLE_DURATION[run_mode]
            duration = cycle_duration * self.run_info.number_of_cycles
            self._sequencing_end_time = start_time + duration
        return self._sequencing_end_time

    @property
    def demultiplexing_started(self):
        if self._demultiplexing_started is None:
            demux_dir = os.path.join(self.path, "./Demultiplexing")
            if os.path.exists(demux_dir):
                self._demultiplexing_started = datetime.datetime.fromtimestamp(os.path.getmtime(demux_dir))
        return self._demultiplexing_started

    @property
    def demultiplexing_done(self):
        if self._demultiplexing_done is None:
            if self.demultiplexing_started:
                demux_file = os.path.join(self.path, "./Demultiplexing/Stats/ConversionStats.xml")
                if os.path.exists(demux_file):
                    self._demultiplexing_done = datetime.datetime.fromtimestamp(os.path.getmtime(demux_file))
        return self._demultiplexing_done

    @property
    def demultiplexing_end_time(self):
        if self._demultiplexing_end_time is None:
            if self.demultiplexing_started:
                self._demultiplexing_end_time = self.demultiplexing_started + DURATIONS['DEMULTIPLEXING']
        return self._demultiplexing_end_time

    @property
    def transfering_started(self):
        if self._transfering_started is None:
            pass
        return self._transfering_started




    def _check_demultiplexing(self):
        if self.status == FC_STATUSES['DEMULTIPLEXING']:
            current_time = datetime.datetime.now()
            if self.demultiplexing_end_time > current_time + datetime.timedelta(hours=1):
                self.warning = "Demultiplexing takes too long"
                self.check_status = True
        return self.check_status

    def _check_transferring(self):
        if self.status == FC_STATUSES['TRANFERRING']:
            current_time = datetime.datetime.now()
            if self.transfering_end_time > current_time + datetime.timedelta(hours=1):
                self.warning = "Transferring takes too long"
                self.check_status = True
        return self.check_status

    def _check_sequencing(self):
        if self.status == FC_STATUSES['SEQUENCING']:
            current_time = datetime.datetime.now()
            if self.cycle_times:
                average_duration = self.cycle_times.average_cycle_time
                last_cycle = self.cycle_times.last_cycle
                last_change = last_cycle['end'] or last_cycle['start']  # if cycle has not finished yet, take start time

                current_duration = current_time - last_change

                if current_duration > average_duration + datetime.timedelta(hours=1):
                    self.warning = "Cycle {} lasts too long.".format(last_cycle['cycle_number'])
                    self.check_status = True
            else:
                if current_time > self._sequencing_end_time():
                    self.warning = 'Sequencing lasts too long. Check status'
                    self.check_status = True
        return self.check_status


    # def get_formatted_description(self):
    #     description = """
    # Date: {date}
    # Flowcell: {flowcell}
    # Instrument: {instrument}
    # Preprocessing server: {localhost}
    # Lanes: {lanes}
    # Tiles: {tiles}
    # Reads: {reads}
    # Index: {index}
    # Chemistry: {chemistry}
    #     """.format(
    #             date=self.run_info['Date'],
    #             flowcell=self.run_info['Flowcell'],
    #             instrument=self.run_info['Instrument'],
    #             localhost=socket.gethostname(),
    #             lanes=self.run_info['FlowcellLayout']['LaneCount'],
    #             tiles=self.run_info['FlowcellLayout']['TileCount'],
    #             reads=self.run_info.formatted_reads,
    #             index=self.run_info.formatted_index,
    #             chemistry=self.chemistry,
    #     )
    #     return description
