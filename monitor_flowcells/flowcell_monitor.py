import os
import re
import logging
import socket

from monitor_flowcells.flowcells.base_flowcell import BaseFlowcell, FC_STATUSES
from monitor_flowcells.trello_utils.trello_board import TrelloBoard
from monitor_flowcells.trello_utils.trello_card import TrelloCard



FC_NAME_RE = r'(\d{6})_([ST-]*\w+\d+)_\d+_([AB]?)([A-Z0-9\-]+)'


class FlowcellMonitor(object):
	""" A connector between the filesystem and the Trello board
	"""
	def __init__(self, config):
		self._config = config
		# initialize None values for @property functions
		self._trello_board = None
		self._data_folders = None

	@property
	def config(self):
		return self._config

	@property
	def data_folders(self):
		if not self._data_folders:
			self._data_folders = []
			for folder in self.config.get('data_folders', []):
				if os.path.exists(folder):
					self._data_folders.append(folder)
					logging.debug("Data folder successfully parsed: {}".format(folder))
				else:
					logging.warning("WARNING: data_folder {} does not exist, but specified in the config file".format(folder))
			if self.config.get('data_folders') is None:
				logging.error("'data_folders' must be specified in the config file")
				raise RuntimeError("'data_folders' must be specified in the config file")
		return self._data_folders

	@property
	def trello_board(self):
		if self._trello_board is None:
			self._trello_board = TrelloBoard(self.config)
		return self._trello_board

	def get_running_flowcells(self):
		flowcells = []
		for data_folder in self.config.get('data_folders', []):
			# go through subfolders
			subfolders = filter(os.path.isdir, [os.path.join(data_folder, fc_path) for fc_path in os.listdir(data_folder)])
			for flowcell_path in subfolders:
				# skip non-flowcell foldersd
				if not re.match(FC_NAME_RE, os.path.basename(flowcell_path)):
					logging.warning("Flowcell name doesn't match regex: {}".format(flowcell_path))
					continue

				# depending on the type, return instance of related class (hiseq, hiseqx, miseq, etc)
				flowcell = BaseFlowcell.init_flowcell(path=flowcell_path)
				flowcells.append(flowcell)
		return flowcells

	def get_nosync_flowcells(self):
		flowcells = []
		# check nosync folder
		for data_folder in self.config.get('data_folders', []):
			nosync_folder = os.path.join(data_folder, 'nosync')
			if os.path.exists(nosync_folder):
				# move flowcell to nosync list
				for flowcell_dir in os.listdir(nosync_folder):
					flowcell_path = os.path.join(nosync_folder, flowcell_dir)
					# skip non-flowcell folders
					if not re.match(FC_NAME_RE, os.path.basename(flowcell_path)):
						logging.warning("Flowcell name doesn't match regex: {}".format(flowcell_path))
						continue
					flowcell = BaseFlowcell.init_flowcell(flowcell_path)
					flowcells.append(flowcell)
		return flowcells

	def archive_flowcells(self):
		nosync_cards = self.trello_board.get_cards_by_list_name(FC_STATUSES['NOSYNC'])
		nosync_flowcells = []
		# get the names of the subfolders nosync folder
		for data_folder in self.data_folders:
			nosync_folder = os.path.join(data_folder, FC_STATUSES['NOSYNC']).lower()
			if not os.path.exists(nosync_folder):
				logging.debug("Nosync folder doesn't exist in {}".format(data_folder))
			else:
				nosync_flowcells += os.listdir(nosync_folder)
		# if the flowcell has been removed from nosync folder -> archive
		for card in nosync_cards:
			if card.name not in nosync_flowcells:
				self.trello_board.move_card(card, FC_STATUSES['ARCHIVED'])

	def update_trello_board(self):
		running_flowcells = self.get_running_flowcells()
		self.trello_board.update(running_flowcells)
		nosync_flowcells = self.get_nosync_flowcells()
		self.trello_board.update(nosync_flowcells)
		self.archive_flowcells()
