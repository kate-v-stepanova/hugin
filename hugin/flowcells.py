import os
import socket
import datetime

from flowcell_parser.classes import RunParametersParser, RunInfoParser

class Flowcell(object):
    def __init__(self, status):
        self._status = status

        self._id = None
        self._run_parameters = None
        self._run_info = None

    @property
    def status(self):
        return self._status

    @property
    def list(self):
        return self.status.status


    @property
    def path(self):
        return self._status.path

    @property
    def id(self):
        if self._id is None:
            self._id =  os.path.basename(self.path)
        return self._id

    @property
    def run_info(self):
        if self._run_info is None:
            run_info_path = os.path.join(self.path, 'RunInfo.xml')
            if not os.path.exists(run_info_path):
                raise RuntimeError('RunInfo.xml cannot be found in {}'.format(self.path))

            self._run_info = RunInfoParser(run_info_path).data
        return self._run_info

    @property
    def run_parameters(self):
        if self._run_parameters is None:
            run_parameters_path = os.path.join(self.path, 'runParameters.xml')
            if not os.path.exists(run_parameters_path):
                raise RuntimeError('runParameters.xml cannot be found in {}'.format(self.path))
            self._run_parameters = RunParametersParser(run_parameters_path).data['RunParameters']
        return  self._run_parameters

    @property
    def name(self):
        raise NotImplementedError("@property 'name' must be implemented in subclass {}".format(self.__class__.__name__))

    @classmethod
    def init_flowcell(cls, status):
        flowcell_dir = status.path
        try:
            parser = RunParametersParser(os.path.join(flowcell_dir, 'runParameters.xml'))
            # print rp.data

        except OSError:
            raise RuntimeError("Cannot find the runParameters.xml file at {}. This is quite unexpected.".format(flowcell_dir))
        else:
            try:
                runtype = parser.data['RunParameters']["Setup"]["Flowcell"]
            except KeyError:
                # logger.warn("Parsing runParameters to fecth instrument type, not found Flowcell information in it. Using ApplicaiotnName")
                runtype = parser.data['RunParameters']['Setup'].get("ApplicationName", '')

            # depending on the type of flowcell, return instance of related class
            if "HiSeq X" in runtype:
                return HiseqXFlowcell(status)
            elif "MiSeq" in runtype:
                return MiseqRun(status)
            elif "HiSeq" in runtype or "TruSeq" in runtype:
                return HiseqRun(status)
            else:
                raise RuntimeError("Unrecognized runtype {} of run {}. Someone as likely bought a new sequencer without telling it to the bioinfo team".format(runtype, flowcell_dir))

    def get_formatted_description(self):
        raise NotImplementedError('get_formatted_description() must be implemented in {}'.format(self.__class__.__name__))


class HiseqXFlowcell(Flowcell):
    def __init__(self, status):
        super(HiseqXFlowcell, self).__init__(status)


    @property
    def full_name(self):
        return os.path.basename(self.status.path)

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
        return Flowcell.run_parameters.fget(self)['Setup']

    def get_formatted_description(self):
        print self.name
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

    @property
    def name(self):
        # todo: returns the wrong name
        return self.run_info['Flowcell']


# class HiseqRun(Run):
#     def __init__(self, flowcell_dir):
#         super(HiseqRun, self).__init__(flowcell_dir)
#
#     @property
#     def name(self):
#         # todo: if 'Flowcell' not in RunInfo?
#         return self.run_info.get('Flowcell')
#
#
#
#
# class MiseqRun(Run):
#     def __init__(self, flowcell_dir):
#         super(MiseqRun, self).__init__(flowcell_dir)
#
#     @property
#     def name(self):
#         # todo: if 'Flowcell' not in RunInfo?
#         return self.run_info['Flowcell']
#
#     @property
#     def chemistry(self):
#         return self.run_parameters['Chemistry']
#
#     @property
#     def formatted_reads(self):
#         # get number of cycles for all reads if read is NOT index
#         reads = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] != 'Y']
#
#         # if only one read
#         if len(reads) == 1:
#             return reads[0]
#         # if all values are the same
#         elif len(set(reads)) == 1:
#             return "{}x{}".format(len(reads), reads[0])
#         # if there are different values
#         else:
#             # '/' will separate the values
#             return "/".join(reads)
#
#     @property
#     def formatted_index(self):
#         # get number of cycles for all reads if read IS index
#         indices = [read['NumCycles'] for read in self.run_info['Reads'] if read['IsIndexedRead'] == 'Y']
#
#         # if only one index
#         if len(indices) == 1:
#             return indices[0]
#         # if more than one index and all values are the same
#         elif len(set(indices)) == 1:
#             return "{}x{}".format(len(indices), indices[0])
#         # if there are different values
#         else:
#             return "/".join(read for read in indices)
#
#
#     def get_formatted_description(self):
#         description = """
#     Date: {date}
#     Flowcell: {flowcell}
#     Instrument: {instrument}
#     Preprocessing server: {localhost}
#     Lanes: {lanes}
#     Tiles: {tiles}
#     Reads: {reads}
#     Indices: {index}
#     Chemistry: {chemistry}
#         """.format(
#                     date=self.run_info['Date'],
#                     flowcell=self.run_info['Flowcell'],
#                     instrument=self.run_info['Instrument'],
#                     localhost=socket.gethostname(),
#                     lanes=self.run_info['FlowcellLayout']['LaneCount'],
#                     tiles=self.run_info['FlowcellLayout']['TileCount'],
#                     reads=self.formatted_reads,
#                     index=self.formatted_reads,
#                     chemistry=self.chemistry,
#         )
#         return description