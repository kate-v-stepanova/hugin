import os


class FlowcellStatus(object):
    def __init__(self, flowcell_path):
        self._path = flowcell_path

        # flowcell statuses
        self.statuses = {
            'ABORTED'       : "Aborted",         # something went wrong in the FC
            'CHECKSTATUS'   : "Check status",    # demultiplex failure
            'SEQUENCING'    : "Sequencing",      # under sequencing
            'DEMULTIPLEXING': "Demultiplexing",  # under demultiplexing
            'TRANFERRING'   : "Transferring",    # tranferring to HPC resource
            # todo: what about NOSYNC?
        }
        #
        self._sequencing_done       = None
        self._demultiplexing_done   = None
        self._transfering_done      = None
        self._demultiplexing_started = None
        self._transfering_started   = None

        # static values
        self.demux_file = "./Demultiplexing/Stats/ConversionStats.xml"
        self.demux_dir = "./Demultiplexing"
        self.transfering_file = "~.logs/transfer.tsv"

        self._status = None
        # message if status is 'CHECKSTATUS'
        self._warning = None

    @property
    def status(self):
        if self._status is None:
            if self.sequencing_done and not self.demultiplexing_started:
                self._status = self.statuses['CHECKSTATUS']
                self._warning = "Sequencing done, demultiplexing not started"

            elif self._demultiplexing_done and not self.transfering_started:
                self._status = self.statuses['CHECKSTATUS']
                self._warning = "Demultiplexing done, transfering not started"
            elif not self.sequencing_done:
                self._status = self.statuses['SEQUENCING']
            elif self.sequencing_done and not self.demultiplexing_done:
                self._status = self.statuses['DEMULTIPLEXING']
            elif self.demultiplexing_done and not self.transfering_done:
                self._status = self.statuses['TRANFERRING']
            else:
                raise RuntimeError('Status undefined. Think more, you developer!')

        return self._status

    @property
    def warning(self):
        return self._warning

    @property
    def path(self):
        return self._path

    @property
    def sequencing_done(self):
        if self._sequencing_done is None:
            # if RTAcomplete.txt is present, sequencing is done
            rta_file = os.path.join(self.path, 'RTAcomplete.txt')
            self._sequencing_done = os.path.exists(rta_file)
        return self._sequencing_done

    @property
    def demultiplexing_done(self):
        if self._demultiplexing_done is None:
            demux_file = os.path.join(self.path, self.demux_file)
            self._demultiplexing_done = os.path.exists(demux_file)
        return self._demultiplexing_done

    @property
    def transfering_done(self):
        if self._transfering_done is None:
            transfering_file = os.path.join(self.path, self.transfering_file)
            self._transfering_done = os.path.exists(transfering_file)
        return self._transfering_done

    @property
    def demultiplexing_started(self):
        if self._demultiplexing_started is None:
            self._demultiplexing_started = os.path.exists(os.path.join(self.path, self.demux_dir))
        return self._demultiplexing_started

    @property
    def transfering_started(self):
        # todo: implement
        return False

