from flowcell_parser.classes import RunParametersParser

class RunParameters:
    def __init__(self, flowcell_dir):
        self._path = flowcell_dir

    @property
    def path(self):
        return self._path