import trello
import logging

class TrelloCard(object):
	def __init__(self, trello_board, flowcell):
		self._trello_board = trello_board
		self._flowcell = flowcell

	@property
	def trello_board(self):
		return self._trello_board

	@property
	def flowcell(self):
		return self._flowcell

	@property
	def trello_card(self):
		if self._trello_card is None:
			self._trello_card = self.trello_board.get_card_by_name(self.flowcell.name).trello_card
		return self._trello_card


	@classmethod
	def init_from_flowcell(cls, flowcell):
		pass

	@classmethod
	def init_from_trello_card(cls, trello_card):
		pass


	@property
	def name(self):
		return self.trello_card.name