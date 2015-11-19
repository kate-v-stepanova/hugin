import os
import datetime

from proper_implementation.wrappers.run_info import RunInfoWrapper
from proper_implementation.wrappers.run_parameters import RunParametersWrapper
from proper_implementation.wrappers.cycle_times import CycleTimesWrapper
from proper_implementation.wrappers.sample_sheet import SampleSheetWrapper

# flowcell statuses
FC_STATUSES =  {
	'ABORTED'       : "Aborted",		 # something went wrong in the FC
	'CHECKSTATUS'   : "Check status",	# demultiplex failure
	'SEQUENCING'	: "Sequencing",	  # under sequencing
	'DEMULTIPLEXING': "Demultiplexing",  # under demultiplexing
	'TRANFERRING'   : "Transferring",	# tranferring to HPC resource
	'NOSYNC'		: "Nosync",		  # in nosync folder
	'ARCHIVED'      : 'Archived',		# removed from nosync folder
}

class BaseFlowcell(object):
	def __init__(self, path):
		self._path = path

		# wrappers
		self._run_parameters = None
		self._run_info = None
		self._cycle_times = None
		self._sample_sheet = None

		# flowcell statuses: timestamp or None
		self._sequencing_started = None
		self._sequencing_done = None
		self._demultiplexing_started = None
		self._demultiplexing_done = None
		self._transfering_started = None
		self._transfering_done = None

		# depending on the statuses above: string
		self._status = None
		# string with warning, or None if status is OK
		self._check_status = None


		# static values
		self.demux_file = "./Demultiplexing/Stats/ConversionStats.xml"
		self.demux_dir = "./Demultiplexing"
		self.cycle_times_file = "Logs/CycleTimes.txt"

	@property
	def path(self):
		return self._path

	@property
	def run_info(self):
		if self._run_info is None:
			run_info_path = os.path.join(self.path, 'RunInfo.xml')
			if not os.path.exists(run_info_path):
				raise RuntimeError('RunInfo.xml cannot be found in {}'.format(self.path))

			self._run_info = RunInfoWrapper(run_info_path)
		return self._run_info

	@property
	def run_parameters(self):
		if self._run_parameters is None:
			run_parameters_path = os.path.join(self.path, 'runParameters.xml')
			if not os.path.exists(run_parameters_path):
				raise RuntimeError('runParameters.xml cannot be found in {}'.format(self.path))
			self._run_parameters = RunParametersWrapper(run_parameters_path)
		return  self._run_parameters

	@property
	def cycle_times(self):
		if self._cycle_times is None:
			cycle_times_path = os.path.join(self.path, 'Logs', 'CycleTimes.txt')
			if os.path.exists(cycle_times_path):
				self._cycle_times = CycleTimesWrapper(cycle_times_path)
			else:
				# todo: logging.warning()
				print "WARNING: CycleTimes.txt does not exist"
		return self._cycle_times

	@property
	def sample_sheet(self):
		if self._sample_sheet is None:
			sample_sheet_path = os.path.join(self.path, 'SampleSheet.csv')
			if os.path.exists(sample_sheet_path):
				self._sample_sheet = SampleSheetWrapper(sample_sheet_path)
			else:
				# todo: logging.warning()
				print "WARNING: SampleSheet.csv does not exist"
		return self._sample_sheet

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
	def demultiplexing_started(self):
		if self._demultiplexing_started is None:
			demux_dir = os.path.join(self.path, self.demux_dir)
			if os.path.exists(demux_dir):
				self._demultiplexing_started = datetime.datetime.fromtimestamp(os.path.getctime(demux_dir))
		return self._demultiplexing_started

	@property
	def demultiplexing_done(self):
		if self._demultiplexing_done is None:
			if self.demultiplexing_started:
				demux_file = os.path.join(self.path, self.demux_file)
				if os.path.exists(demux_file):
					self._demultiplexing_done = datetime.datetime.fromtimestamp(os.path.getmtime(demux_file))
		return self._demultiplexing_done

	@property
	def transfering_started(self):
		if self._transfering_started is None:
			pass
			# command = "{ls} {path}".format(path=config['transfering']['path'])
			# proc = subprocess.Popen(['ssh', '-t', '{}@{}' %(config['user'], server_url), command],

			# transfering_file = os.path.join(self.path, self.transfering_file)
			# if os.path.exists(transfering_file):
			#     self._transfering_started = datetime.datetime.fromtimestamp(os.path.getctime(transfering_file))

		return self._transfering_started

	@property
	def transfering_done(self):
		if self._transfering_done is None:
			if self.transfering_started:
				# todo: moved to nosync
				pass
		return self._transfering_done