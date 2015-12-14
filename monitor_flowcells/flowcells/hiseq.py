import logging
import os
import datetime

from flowcell_parser.classes import SampleSheetParser

from utils.config.config import CONFIG as config
from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell, CYCLE_DURATION


class HiseqFlowcell(BaseFlowcell):
	@property
	def sample_sheet(self):
		if self._sample_sheet is None:
			sample_sheet_path = os.path.join(self.path, 'SampleSheet.csv')
			if os.path.exists(sample_sheet_path):
				self._sample_sheet = SampleSheetParser(sample_sheet_path).data
			else:
				logging.warning("SampleSheet.csv does not exist: {}".format(sample_sheet_path))
				path = config.get('sample_sheet_path', {}).get('hiseq')
				if path is None:
					logging.error("'sample_sheet_path' missing in the config file")
					raise RuntimeError("'sample_sheet_path' missing in the config file: {}".format(config.get('config_path')))
				else:
					sample_sheet_path = os.path.join(path, self.name, 'SampleSheet.csv')
					if os.path.exists(sample_sheet_path):
						self._sample_sheet = SampleSheetParser(os.path.join(sample_sheet_path, 'SampleSheet.csv')).data
					else:
						logging.error("SampleSheet.csv does not exist at {}".format(os.path.join(path, self.name)))
						raise RuntimeError("SampleSheet.csv does not exist at {}".format(os.path.join(path, self.name)))
		return self._sample_sheet

	@property
	def transfering_started(self):
		return self._transfering_started

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
	def number_of_cycles(self):
		if self.cycle_times:
			return self.cycle_times[-1]['cycle_number'] # not number of cycles, but the last cycle!!
		return None

	@property
	def first_cycle(self):
		if self.cycle_times:
			return self.cycle_times[0]
		return None

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
	def chemistry(self):
		return self.run_parameters['ChemistryVersion']

	@property
	def projects(self):
		projects = []
		for sample in self.sample_sheet:
			project = sample['SampleProject']
			if project not in projects:
				projects.append(project)
		return projects