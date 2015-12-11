import os
import datetime
import logging
import socket
import subprocess

from utils.config.config import CONFIG as config

# from monitor_flowcells.wrappers.run_info import RunInfoWrapper
# from monitor_flowcells.wrappers.run_parameters import RunParametersWrapper
# from monitor_flowcells.wrappers.cycle_times import CycleTimesWrapper
# from monitor_flowcells.wrappers.sample_sheet import SampleSheetWrapper

from flowcell_parser.classes import RunInfoParser, RunParametersParser, CycleTimesParser, SampleSheetParser

# flowcell statuses
FC_STATUSES =  {
	'ABORTED'	   : "Aborted",		 # something went wrong in the FC
	'CHECKSTATUS'   : "Check status",	# demultiplex failure
	'SEQUENCING'	: "Sequencing",	  # under sequencing
	'DEMULTIPLEXING': "Demultiplexing",  # under demultiplexing
	'TRANFERRING'   : "Transferring",	# tranferring to HPC resource
	'NOSYNC'		: "Nosync",		  # in nosync folder
	'ARCHIVED'	  : 'Archived',		# removed from nosync folder
}

CYCLE_DURATION = {
	'RapidRun'		  : datetime.timedelta(minutes=12),
	'HighOutput'		: datetime.timedelta(minutes=100),
	'RapidHighOutput'   : datetime.timedelta(minutes=43),
	'MiSeq'			 : datetime.timedelta(minutes=6),
	'HiSeqX'			: datetime.timedelta(minutes=10),
}

DURATIONS = {
	'DEMULTIPLEXING'	: datetime.timedelta(hours=4),
	'TRANSFERING'	   : datetime.timedelta(hours=12)
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

		# expected end times:
		self._sequencing_end_time = None
		self._demultiplexing_end_time = None
		self._transfering_end_time = None
		self._due_date = None

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

			self._run_info = RunInfoParser(run_info_path).data
		return self._run_info

	@property
	def run_parameters(self):
		if self._run_parameters is None:
			run_parameters_path = os.path.join(self.path, 'runParameters.xml')
			if not os.path.exists(run_parameters_path):
				raise RuntimeError('runParameters.xml cannot be found in {}'.format(self.path))
			self._run_parameters = RunParametersParser(run_parameters_path).data['RunParameters']['Setup']
		return  self._run_parameters

	@property
	def cycle_times(self):
		if self._cycle_times is None:
			cycle_times_path = os.path.join(self.path, 'Logs', 'CycleTimes.txt')
			if os.path.exists(cycle_times_path):
				self._cycle_times = CycleTimesParser(cycle_times_path).cycles
			else:
				logging.warning("CycleTimes.txt does not exist at {}".format(cycle_times_path))
		return self._cycle_times

	@property
	def sample_sheet(self):
		return NotImplementedError('sample_sheet @property must be implemented in the class {}'.format(self.__class__.__name__))

	@property
	def name(self):
		return os.path.basename(self.path)

	@property
	def status(self):
		if self._status is None:
			if os.path.basename(os.path.dirname(self.path)) == 'nosync':
				self._status = FC_STATUSES['NOSYNC']

			elif self.transfering_started and not self.transfering_done:
				self._status = FC_STATUSES['TRANFERRING']

			elif self.demultiplexing_done and not self.transfering_started:
				# todo: check status or demultiplexing ?
				self._status = FC_STATUSES['DEMULTIPLEXING']

			elif self.demultiplexing_started and not self.demultiplexing_done:
				self._status = FC_STATUSES['DEMULTIPLEXING']

			elif self.sequencing_started and not self.sequencing_done:
				self._status = FC_STATUSES['SEQUENCING']

			else:
				logging.warning('Status undefined. Flowcell: {}'.format(self.path))
				logging.debug('Sequencing started: {} \nSequencing done: {} \Demultiplexing started: {}\n Demultiplexing done: {}\n Transferring started: {} \n Transferring done: {}'.format(
					self.sequencing_started, self.sequencing_done, self.demultiplexing_started, self.demultiplexing_done, self.transfering_started, self.transfering_done
				))

		# use carefully (@property or _variable), to avoid infinite recursion
		if self.check_status:
			self._status = FC_STATUSES['CHECKSTATUS']

		return self._status

	@property
	def check_status(self):
		# warning: call check_status after status, otherwise None.
		if self._check_status is None:
			now = datetime.datetime.now()
			# todo: add additional time
			if self.due_date and self.due_date < now:
				if self._status == FC_STATUSES['DEMULTIPLEXING'] or self._status == FC_STATUSES['TRANFERRING']:
					self._check_status = "STATUS: {}, started: {}, expected end time: {}, current time: {}".format(
						self._status, self.transfering_started or self.demultiplexing_started,
						self.transferring_end_time or self.demultiplexing_end_time,	now
					)
				elif self._status == FC_STATUSES['SEQUENCING']:
					if self.cycle_times:
						self._check_status = "STATUS: {}, started: {}, expected end time: {}, current time: {}, current cycle: {}".format(
							self._status, self.sequencing_started, self.sequencing_end_time, now, self.last_cycle_number
						)
		return self._check_status

	@property
	def sequencing_started(self):
		if self._sequencing_started is None:
			self._sequencing_started = datetime.datetime.fromtimestamp(os.path.getctime(self.path))
		return self._sequencing_started

	@property
	def sequencing_done(self):
		if self._sequencing_done is None:
			# todo: check how many cycles left
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
	def transfering_done(self):
		if self._transfering_done is None:
			if self.transfering_started:
				# todo: moved to nosync
				pass
		return self._transfering_done

	@property
	def due_date(self):
		if self._due_date is None:
			self._due_date = self.transferring_end_time or self.demultiplexing_end_time or self.sequencing_end_time

		# if self._status == FC_STATUSES['SEQUENCING']:
		# 	self._due_date = self.sequencing_end_time
		# elif self._status == FC_STATUSES['DEMULTIPLEXING']:
		# 	self._due_date = self.demultiplexing_end_time
		# elif self._status == FC_STATUSES['TRANFERRING']:
		# 	self._due_date = self.transferring_end_time
		return self._due_date

	@classmethod
	def init_flowcell(cls, path):
		try:
			parser = RunParametersParser(os.path.join(path, 'runParameters.xml'))
			# print rp.data

		except OSError:
			raise RuntimeError("Cannot find the runParameters.xml file at {}. This is quite unexpected.".format(path))
		else:
			try:
				runtype = parser.data['RunParameters']["Setup"]["Flowcell"]
			except KeyError:
				# logger.warn("Parsing runParameters to fecth instrument type, not found Flowcell information in it. Using ApplicaiotnName")
				runtype = parser.data['RunParameters']['Setup'].get("ApplicationName", '')

			# depending on the type of flowcell, return instance of related class
			if "HiSeq X" in runtype:
				# import has to be here to avoid ImportError (python modules cannot import each other)
				import monitor_flowcells.flowcells.hiseqx as hiseqx
				return hiseqx.HiseqxFlowcell(path)
			elif "MiSeq" in runtype:
				import monitor_flowcells.flowcells.miseq as miseq
				return miseq.MiseqFlowcell(path)
			elif "HiSeq" in runtype or "TruSeq" in runtype:
				import monitor_flowcells.flowcells.hiseq as hiseq
				return hiseq.HiseqFlowcell(path)
			else:
				raise RuntimeError("Unrecognized runtype {} of run {}. Someone as likely bought a new sequencer without telling it to the bioinfo team".format(runtype, path))

	@property
	def demultiplexing_end_time(self):
		if self._demultiplexing_end_time is None:
			if self.demultiplexing_started is not None:
				self._demultiplexing_end_time = self.demultiplexing_started + DURATIONS['DEMULTIPLEXING']
		return self._demultiplexing_end_time

	@property
	def transferring_end_time(self):
		if self._transfering_end_time is None:
			if self.transfering_started is not None:
				self._transfering_end_time = self.transfering_started + DURATIONS['TRANSFERING']
		return self._transfering_end_time

	@property
	def sequencing_end_time(self):
		if self._sequencing_end_time is None:
			if self.cycle_times is None:
				start_time = self.sequencing_started
				run_mode = self.run_mode
				duration = CYCLE_DURATION[run_mode] * self.number_of_cycles # todo: das ist None
				self._sequencing_end_time = start_time + duration
			else:
				duration = self.average_cycle_time * self.number_of_cycles
				start_time = self.first_cycle['start']
				self._sequencing_end_time = start_time + duration
		return self._sequencing_end_time

	@property
	def description(self):

		def formatted_reads(list_of_reads):
			# if only one index
			if len(list_of_reads) == 1:
				return list_of_reads[0]
			# if more than one index and all values are the same
			elif len(set(list_of_reads)) == 1:
				return "{}x{}".format(len(list_of_reads), list_of_reads[0])
			# if there are different values
			else:
				return "/".join(read for read in list_of_reads)

		description = """\tDate: {date}
	Flowcell: {flowcell}
	Instrument: {instrument}
	Preprocessing server: {localhost}
	Lanes: {lanes}
	Tiles: {tiles}
	Reads: {reads}
	Index: {index}
	Chemistry: {chemistry}
	Projects: {projects}""".format(
                date=self.date,
                flowcell=self.name,
                instrument=self.instrument,
                localhost=socket.gethostname(),
                lanes=self.lane_count,
                tiles=self.tile_count,
                reads=formatted_reads(self.reads),
                index=formatted_reads(self.indexes),
                chemistry=self.chemistry,
				projects=";".join(project for project in set(self.projects)),
        )
		return description

	def __eq__(self, other):
		return self.path == other.path
