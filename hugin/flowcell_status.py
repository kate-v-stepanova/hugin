import os


# flowcell statuses
FC_STATUSES =  {
    'ABORTED'       : "Aborted",         # something went wrong in the FC
    'CHECKSTATUS'   : "Check status",    # demultiplex failure
    'SEQUENCING'    : "Sequencing",      # under sequencing
    'DEMULTIPLEXING': "Demultiplexing",  # under demultiplexing
    'TRANFERRING'   : "Transferring",    # tranferring to HPC resource
    'NOSYNC'        : "Nosync",
    'ARCHIVED'      : 'Archived',
    # todo: what about NOSYNC?
}


class FlowcellStatus(object):
    def __init__(self, flowcell_path):
        self._path = flowcell_path

        # statuses
        self._sequencing_done       = None
        self._demultiplexing_done   = None
        self._transfering_done      = None
        self._demultiplexing_started = None
        self._transfering_started   = None
        self._nosync = None

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
            if os.path.basename(os.path.dirname(self.path)) == 'nosync':
                self._nosync = True
                self._status = FC_STATUSES['NOSYNC']

            # elif self.sequencing_done and not self.demultiplexing_started:
            #     self._status = FC_STATUSES['CHECKSTATUS']
            #     self._warning = "Sequencing done, demultiplexing not started"
            #
            # elif self._demultiplexing_done and not self.transfering_started:
            #     self._status = FC_STATUSES['CHECKSTATUS']
            #     self._warning = "Demultiplexing done, transfering not started"
            elif not self.sequencing_done:
                self._status = FC_STATUSES['SEQUENCING']
            elif self.sequencing_done and not self.demultiplexing_done:
                self._status = FC_STATUSES['DEMULTIPLEXING']
            elif self.demultiplexing_done and not self.transfering_done:
                self._status = FC_STATUSES['TRANFERRING']
            else:
                raise RuntimeError('Status undefined. Think more, you developer!')

        return self._status

    @property
    def nosync(self):
        if self._nosync is None:
            self._nosync = os.path.basename(os.path.dirname(self.path)).lower() == 'nosync'
        return self._nosync

    @property
    def warning(self):
        return self._warning

    @property
    def path(self):
        return self._path

    @property
    def sequencing_done(self):
        if self._sequencing_done is None:
            # if RTAComplete.txt is present, sequencing is done
            rta_file = os.path.join(self.path, 'RTAComplete.txt')
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
        raise NotImplementedError('FlowcellStatus.transfering done has not been implemented in {}'.format(self.__class__.__name__))

    @property
    def demultiplexing_started(self):
        if self._demultiplexing_started is None:
            self._demultiplexing_started = os.path.exists(os.path.join(self.path, self.demux_dir))
        return self._demultiplexing_started

    @property
    def transfering_started(self):
        if self._transfering_started is None:
            transfering_file = os.path.join(self.path, self.transfering_file)
            self._transfering_started = os.path.exists(transfering_file)
        return self._transfering_started

