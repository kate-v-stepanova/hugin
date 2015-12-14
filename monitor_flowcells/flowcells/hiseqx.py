import datetime
import time
import os
import logging
import subprocess

from flowcell_parser.classes import SampleSheetParser

from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell
from monitor_flowcells.flowcells.base_flowcell import CYCLE_DURATION

from utils.config.config import CONFIG as config

class HiseqxFlowcell(BaseFlowcell):
	@property
	def chemistry(self):
		return self.run_parameters['ChemistryVersion']

	@property
	def short_name(self):
		# todo: returns the wrong name
		return self.run_info['Flowcell']

	@property
	def date(self):
		return self.run_info['Date']

	@property
	def instrument(self):
		return self.run_info['Instrument']

	@property
	def lane_count(self):
		return self.run_info['FlowcellLayout']['LaneCount']

	@property
	def tile_count(self):
		return self.run_info['FlowcellLayout']['TileCount']

	@property
	def reads(self):
		# get number of cycles for all reads if read is NOT index
		result = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] != 'Y']
		return result

	@property
	def indexes(self):
		# get number of cycles for all reads if read IS index
		result = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] == 'Y']
		return result

	@property
	def run_mode(self):
		return self.run_parameters['RunMode']
	
	@property
	def average_cycle_time(self):
		if self.cycle_times:
			sum_duration = datetime.timedelta(0)
			for cycle in self.cycle_times:
				duration = cycle['end'] - cycle['start']
				sum_duration += duration

			if len(self.cycle_times) > 10:
				return sum_duration / len(self.cycle_times)

		return CYCLE_DURATION[self.run_mode]

	@property
	def last_cycle(self):
		if self.cycle_times:
			return self.cycle_times[-1]
		return None

	@property
	def last_cycle_number(self):
		if self.cycle_times:
			return self.cycle_times[-1]['cycle_number']
		return None

	@property
	def first_cycle(self):
		if self.cycle_times:
			return self.cycle_times[0]
		return None

	@property
	def number_of_cycles(self):
		return len(self.cycle_times) if self.cycle_times else None

	@property
	def projects(self):
		projects = []
		for lane in self.sample_sheet:
			project = lane['Project']
			if project not in projects:
				projects.append(project)
		return projects


	@property
	def sample_sheet(self):
		if self._sample_sheet is None:
			sample_sheet_path = os.path.join(self.path, 'SampleSheet.csv')
			if os.path.exists(sample_sheet_path):
				self._sample_sheet = SampleSheetParser(sample_sheet_path).data
			else:
				logging.warning("SampleSheet.csv does not exist: {}".format(os.path.abspath(sample_sheet_path)))
				path = config.get('sample_sheet_path', {}).get('hiseqx')
				if path is None:
					logging.error("'sample_sheet_path' missing in the config file")
					raise RuntimeError("'sample_sheet_path' missing in the config file: {}".format(config.get('config_path')))
				else:
					sample_sheet_path = os.path.join(path, self.name, 'SampleSheet.csv')
					if os.path.exists(sample_sheet_path):
						self._sample_sheet = SampleSheetParser(sample_sheet_path).data
					else:
						logging.error("SampleSheet.csv does not exist at {}".format(sample_sheet_path))
						raise RuntimeError("SampleSheet.csv does not exist at {}".format(sample_sheet_path))
		return self._sample_sheet


	@property
	def number_of_samples(self):
		return len(self.sample_sheet)

	@property
	def transfering_started(self):
		# if self._transfering_started is None:
		# 	transfering= config.get('transfering')
		# 	if transfering is None:
		# 		logging.error("'transferring is missing in the config file: {}".format(config['config_path']))
		# 		raise RuntimeError("'transferring is missing in the config file: {}".format(config['config_path']))
		# 	hiseq = transfering.get('hiseqx')
		# 	if hiseq is None:
		# 		logging.error("'transferring configuration contains no 'hiseq' parameter: {}".format(config['config_path']))
		# 		raise RuntimeError("'transferring configuration contains no 'hiseq' parameter: {}".format(config['config_path']))
		# 	url = hiseq.get('url')
		# 	username = hiseq.get('username')
		# 	path = hiseq.get('path')
		# 	if any((url is None, username is None, path is None)):
		# 		logging.error("config.transfering.hiseq must specify url, username and password. Config file: {}".format(config['config_path']))
		# 		raise RuntimeError("config.transfering.hiseq must specify url, username and password. Config file: {}".format(config['config_path']))
		# 	path = os.path.join(path, self.name)
		#
		# 	# path = "/home/ekat"
		# 	exist = "Transfering has been started at: "
		# 	doesnt = "Transfering has not been started'"
		# 	command = "python -c \"import os; print '{exists}' + str(os.path.getctime('{path}')) if os.path.exists('{path}') else '{doesnt}\"".format(path=path, exists=exist, doesnt=doesnt)
		#
		# 	try:
		# 		ssh = subprocess.Popen(['ssh', '-t', '{}@{}'.format(username, url), command],
	     #                   stdout=subprocess.PIPE,
	     #                   stderr=subprocess.PIPE)
		# 		result = ssh.communicate()
		# 		output = result[0]
		# 		if exist in result[0]:
		# 			started = float(output.strip().strip(exist))
		# 		self._transfering_started = datetime.datetime.fromtimestamp(started)
		# 	except Exception as e:
		# 		logging.error("Could not connect to ssh: {}@{}".format(username, url))
		# 		logging.error(e)
		#
		# 	# todo: optimize! Now each flowcell connects to ssh to define due_time -> no need if status is sequencing

		return self._transfering_started