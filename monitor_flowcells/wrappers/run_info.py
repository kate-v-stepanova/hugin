from flowcell_parser.classes import RunInfoParser


class RunInfoWrapper(RunInfoParser):

	@property
	def flowcell(self):
		# date=self.run_info.date,
		# flowcell=self.name,
		# instrument=self.run_info.instrument,
		# localhost=socket.gethostname(),
		# lanes=self.run_info.lane_count, #['FlowcellLayout']['LaneCount'],
		# tiles=self.run_info.tile_count, #['FlowcellLayout']['TileCount'],
		# reads=self.run_info.formatted_reads,
		# index=self.run_info.formatted_index,
		# chemistry=self.run_info.chemistry,

		return self.data['Flowcell']
	
	@property
	def date(self):
		return self.data['Date']
	
	@property
	def instrument(self):
		return self.data['Instrument']
	
	@property
	def lane_count(self):
		return self.data['FlowcellLayout']['LaneCount']
	
	@property
	def tile_count(self):
		return self.data['FlowcellLayout']['TileCount']

	@property
	def reads(self):
		# get number of cycles for all reads if read is NOT index
		result = [read['NumCycles'] for read in self.data['Reads'] if read['IsIndexedRead'] != 'Y']
		return result

	@property
	def indexes(self):
		# get number of cycles for all reads if read IS index
		result = [read['NumCycles'] for read in self.data['Reads'] if read['IsIndexedRead'] == 'Y']
		return result

	@property
	def chemistry(self):
		return self.data['ChemistryVersion']

