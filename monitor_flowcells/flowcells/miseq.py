import logging
import os
from utils.config.config import CONFIG as config

from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell
from flowcell_parser.classes import SampleSheetParser


class MiseqFlowcell(BaseFlowcell):
	@property
	def sample_sheet(self):
		if self._sample_sheet is None:
			sample_sheet_path = os.path.join(self.path, 'SampleSheet.csv')
			if os.path.exists(sample_sheet_path):
				self._sample_sheet = SampleSheetParser(sample_sheet_path).data
			else:
				logging.warning("SampleSheet.csv does not exist: {}".format(sample_sheet_path))
				path = config.get('sample_sheet_path', {}).get('hiseqx')

				if path is None:
					logging.error("'sample_sheet_path' missing in the config file")
					raise RuntimeError("'sample_sheet_path' missing in the config file: {}".format(config.get('config_path')))
				else:
					if path.startswith('/'):
						sample_sheet_path = os.path.join(path, self.name, 'SampleSheet.csv')
					else:
						sample_sheet_path = os.path.join(self.path, path, 'SampleSheet.csv')

					if os.path.exists(sample_sheet_path):
						self._sample_sheet = SampleSheetParser(os.path.join(sample_sheet_path, 'SampleSheet.csv')).data
					else:
						logging.error("SampleSheet.csv does not exist at {}".format(os.path.join(path, self.name)))
						raise RuntimeError("SampleSheet.csv does not exist at {}".format(os.path.join(path, self.name)))
		return self._sample_sheet