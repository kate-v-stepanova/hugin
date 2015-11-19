import os
import socket
import datetime

from flowcell_parser.classes import RunParametersParser, RunInfoParser, CycleTimesParser, SampleSheetParser

# from hugin.flowcell_status import FC_STATUSES

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
		self._id = None
		self._run_parameters = None
		self._run_info = None
		self._cycle_times = None
		self._sample_sheet = None


		# statuses:
		# a timestamp when the status has changed
		self._sequencing_started	= None
		self._sequencing_done	   = None
		self._demultiplexing_done   = None
		self._transfering_done	  = None
		self._demultiplexing_started = None
		self._transfering_started   = None
		self._nosync = None
		
		# static values
		self.demux_file = "./Demultiplexing/Stats/ConversionStats.xml"
		self.demux_dir = "./Demultiplexing"
		self.transfering_file = "~.logs/transfer.tsv"
		self.cycle_times_file = "Logs/CycleTimes.txt"

		# flag if the flowcell has the same status too long. contains the warning message
		self._check_status = None

	@property
	def path(self):
		return self._path

	@property
	def trello_list(self):
		if self.check_status:
			return FC_STATUSES['CHECKSTATUS']
		else: return self.status

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
			self._run_parameters = RunParametersParser(run_parameters_path).data['RunParameters']
		return  self._run_parameters

	@property
	def cycle_times(self):
		if self._cycle_times is None:
			cycle_times_path = os.path.join(self.path, 'Logs', 'CycleTimes.txt')
			if os.path.exists(cycle_times_path):
				self._cycle_times = CycleTimesParser(cycle_times_path)
			else:
				# todo: logging.warning()
				print "WARNING: CycleTimes.txt does not exist"
		return self._cycle_times

	@property
	def sample_sheet(self):
		if self._sample_sheet is None:
			sample_sheet_path = os.path.join(self.path, 'SampleSheet.csv')
			if os.path.exists(sample_sheet_path):
				self._sample_sheet = SampleSheetParser(sample_sheet_path)
			else:
				# todo: logging.warning()
				print "WARNING: SampleSheet.csv does not exist"
		return self._sample_sheet


	@classmethod
	def init_flowcell(cls, status):
		# to prevent ImportError, import modules here
		import hugin.flowcells.hiseqx
		import hugin.flowcells.hiseq
		import hugin.flowcells.miseq

		flowcell_dir = status.path
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
				return hugin.flowcells.hiseqx.HiSeqXBaseFlowcell(status) # here can be import error if from bla import HiSeqXFlowcell
			elif "MiSeq" in runtype:
				return hugin.flowcells.miseq.MiSeqBaseFlowcell(status)
			elif "HiSeq" in runtype or "TruSeq" in runtype:
				return hugin.flowcells.hiseq.HiSeqBaseFlowcell(status)
			else:
				raise RuntimeError("Unrecognized runtype {} of run {}. Someone as likely bought a new sequencer without telling it to the bioinfo team".format(runtype, flowcell_dir))

	@property
	def status(self):
		if self._status is None:
			if os.path.basename(os.path.dirname(self.path)) == 'nosync':
				self._nosync = True
				self._status = FC_STATUSES['NOSYNC']
			elif self.transfering_started and not self.transfering_done:
				self._status = FC_STATUSES['TRANFERRING']
			elif self.demultiplexing_started and not self.demultiplexing_done:
				self._status = FC_STATUSES['DEMULTIPLEXING']
			else:
				self._status = FC_STATUSES['SEQUENCING']
		return self._status

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