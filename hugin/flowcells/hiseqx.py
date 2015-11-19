import os
import datetime
import socket

from flowcell_parser.classes import CycleTimesParser

from hugin.flowcells.base_flowcell import BaseFlowcell, FC_STATUSES

class HiSeqXFlowcell(BaseFlowcell):
    # to common class
    @property
    def full_name(self):
        return os.path.basename(self.status.path)

    @property
    def cycle_times(self):
        if self._cycle_times is None:
            cycle_times_path = os.path.join(self.path, 'Logs/CycleTimes.txt')
            if os.path.exists(cycle_times_path):
                # todo: CycleTimesParser fails when no file found
                self._cycle_times = CycleTimesParser(cycle_times_path).cycles
        return self._cycle_times

    @property
    def name(self):
        # todo: returns the wrong name
        return self.run_info['Flowcell']

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

    @property
    def chemistry(self):
        return self.run_parameters['ChemistryVersion']

    @property
    def run_parameters(self):
        # dangerous
        # call run_parameters from the base class
        return BaseFlowcell.run_parameters.fget(self)['Setup']
    #
    @property
    def average_cycle_time(self):
        if self.cycle_times:
            sum_duration = datetime.timedelta(0)
            for cycle in self.cycle_times:
                duration = cycle['end'] - cycle['start']
                sum_duration += duration

            if len(self.cycle_times) < 10:
                # todo: depending on RunMode
                average_duration = CYCLE_DURATION['HiSeqX']
            else:
                average_duration = sum_duration / len(self.cycle_times)
            return average_duration
        return None

    @property
    def due_time(self):
        if self.status.status == FC_STATUSES['SEQUENCING']:
            return self._sequencing_end_time()
        elif self.status.status == FC_STATUSES['DEMULTIPLEXING']:
            return self.status.demultiplexing_end_time
        elif self.status.status == FC_STATUSES['TRANFERRING']:
            return self.status.transfering_end_time
        else:
            raise NotImplementedError('Unknown status: {}. End time for the status not implemented'.format(self.status.status))

    @property
    def number_of_cycles(self):
        number_of_cycles = 0
        for read in self.run_info['Reads']:
            number_of_cycles += int(read['NumCycles'])
        return number_of_cycles

    @property
    def server(self):
        return socket.gethostname()


    def check_status(self):
        if self.status.status == FC_STATUSES['SEQUENCING']:
            return self._check_sequencing()
        elif self.status.status == FC_STATUSES['DEMULTIPLEXING']:
            return self._check_demultiplexing()
        elif self.status.status == FC_STATUSES['TRANFERRING']:
            return self._check_transferring()

    def _check_demultiplexing(self):
        if self.status.status == FC_STATUSES['DEMULTIPLEXING']:
            current_time = datetime.datetime.now()
            if self.status.demultiplexing_end_time > current_time + datetime.timedelta(hours=1):
                self.status.warning = "Demultiplexing takes too long"
                self.status.check_status = True
        return self.status.check_status

    def _check_transferring(self):
        if self.status.status == FC_STATUSES['TRANFERRING']:
            current_time = datetime.datetime.now()
            if self.status.transfering_end_time > current_time + datetime.timedelta(hours=1):
                self.status.warning = "Transferring takes too long"
                self.status.check_status = True
        return self.status.check_status

    def _check_sequencing(self):
        if self.status.status == FC_STATUSES['SEQUENCING']:
            current_time = datetime.datetime.now()
            if self.cycle_times and len(self.cycle_times) > 5:
                average_duration = self.average_cycle_time
                last_cycle = self.cycle_times[-1]
                last_change = last_cycle['end'] or last_cycle['start']  # if cycle has not finished yet, take start time

                current_duration = current_time - last_change

                if current_duration > average_duration + datetime.timedelta(hours=1):
                    self.status.warning = "Cycle {} lasts too long.".format(last_cycle['cycle_number'])
                    self.status.check_status = True
            else:
                if current_time > self._sequencing_end_time():
                    self.status.warning = 'Sequencing lasts too long. Check status'
                    self.status.check_status = True
        return self.status.check_status

    def _sequencing_end_time(self):
        if self.cycle_times is None:
            start_time = self.status.sequencing_started
            # todo duration depending on the run mode!
            duration = CYCLE_DURATION['HiSeqX'] * self.number_of_cycles
            end_time = start_time + duration
        else:
            duration = self.average_cycle_time * self.number_of_cycles
            start_time = self.cycle_times[0]['start']
            end_time = start_time + duration
        return end_time


    def get_formatted_description(self):
        description = """
    Date: {date}
    Flowcell: {flowcell}
    Instrument: {instrument}
    Preprocessing server: {localhost}
    Lanes: {lanes}
    Tiles: {tiles}
    Reads: {reads}
    Index: {index}
    Chemistry: {chemistry}
        """.format(
                date=self.run_info['Date'],
                flowcell=self.run_info['Flowcell'],
                instrument=self.run_info['Instrument'],
                localhost=socket.gethostname(),
                lanes=self.run_info['FlowcellLayout']['LaneCount'],
                tiles=self.run_info['FlowcellLayout']['TileCount'],
                reads=self.formatted_reads,
                index=self.formatted_index,
                chemistry=self.chemistry,
        )
        return description