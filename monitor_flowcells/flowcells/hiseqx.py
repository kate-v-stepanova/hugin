import datetime
from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell
from monitor_flowcells.flowcells.base_flowcell import CYCLE_DURATION

class HiseqxFlowcell(BaseFlowcell):
	@property
	def chemistry(self):
		return self.run_parameters['RunParameters']['Setup']['ChemistryVersion']

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
	def chemistry(self):
		return self.run_info['ChemistryVersion']
	# 
	# @property
	# def cycle_times_start(self):
	# 	if self.cycle_times:
	# 		return self.cycle_times
	# 	
	# 	
	#
	
	@property
	def average_cycle_time(self):
		if self.cycle_times:
			sum_duration = datetime.timedelta(0)
			for cycle in self.cycle_times:
				duration = cycle['end'] - cycle['start']
				sum_duration += duration

			if len(self.cycle_times) > 10:
				return sum_duration / len(self.cycle_times)

		# todo: depending on RunMode
		return CYCLE_DURATION['HiSeqX']

	@property
	def last_cycle(self):
		if self.cycle_times:
			return self.cycle_times[-1]
		return None

	@property
	def first_cycle(self):
		if self.cycle_times:
			return self.cycle_times[0]
		return None

	@property
	def number_of_cycles(self):
		return len(self.cycle_times) if self.cycle_times else None