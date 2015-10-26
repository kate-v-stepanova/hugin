import datetime
import os

from flowcell_parser.classes import CycleTimesParser

class CycleTimes:
    def __init__(self, flowcell_dir):
        self._path = os.path.join(flowcell_dir, 'Logs/CycleTimes.txt')
        self._cycle_times = None

    @property
    def path(self):
        return self._path

    @property
    def cycle_times(self):
        if self._cycle_times is None:
            if os.path.exists(self.path):
                # todo: CycleTimesParser fails when no file found
                self._cycle_times = CycleTimesParser(self.path).cycles
        return self._cycle_times

    @property
    def average_cycle_time(self):
        if self.cycle_times:
            sum_duration = datetime.timedelta(0)
            for cycle in self.cycle_times:
                duration = cycle['end'] - cycle['start']
                sum_duration += duration
            average_duration = sum_duration / len(self.cycle_times)
            return average_duration
        else: return None

    @property
    def last_cycle(self):
        return self.cycle_times[-1]