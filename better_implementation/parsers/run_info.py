import os

from flowcell_parser.classes import RunInfoParser


class RunInfo:
    def __init__(self, flowcell_dir):
        self._path = os.path.join(flowcell_dir, 'RunInfo.xml')
        self._run_info = None

    @property
    def path(self):
        return self._path

    @property
    def run_info(self):
        if self._run_info is None:
            self._run_info = RunInfoParser(self.path)
        return self._run_info

    @property
    def number_of_cycles(self):
        number_of_cycles = 0
        for read in self.run_info['Reads']:
            number_of_cycles += int(read['NumCycles'])
        return number_of_cycles

    @property
    def formatted_reads(self):
        # get number of cycles for all reads if read is NOT index
        reads = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] != 'Y']

        # if only one read
        if len(reads) == 1:
            return reads[0]
        # if all values are the same
        elif len(set(reads)) == 1:
            return "{}x{}".format(len(reads), reads[0])
        # if there are different values
        else:
            # '/' will separate the values
            return "/".join(reads)

    @property
    def formatted_index(self):
        # get number of cycles for all reads if read IS index
        indices = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] == 'Y']

        # if only one index
        if len(indices) == 1:
            return indices[0]
        # if more than one index and all values are the same
        elif len(set(indices)) == 1:
            return "{}x{}".format(len(indices), indices[0])
        # if there are different values
        else:
            return "/".join(read for read in indices)