import trello
import logging
import socket

from monitor_flowcells.flowcells.base_flowcell import FC_STATUSES

class TrelloBoard(object):
	""" Wrapper class to work with Trello objects
	"""
	def __init__(self, config):
			trello_args = config.get('trello')
			# todo check if board exist
			api_key = trello_args.get('api_key')
			token = trello_args.get('token')
			api_secret = trello_args.get('api_secret')
			board_id = trello_args.get('board_id')
			try:
				client = trello.TrelloClient(api_key=api_key, token=token, api_secret=api_secret)
				self._trello_board  = client.get_board(board_id)
			except Exception as e:
				logging.error(e)
				logging.error("Can't connect to the board: {}".format(board_id))
				logging.debug("Trello configuration: {}".format(trello_args))
				raise e

	@property
	def trello_board(self):
		return self._trello_board

	def get_cards_by_list_name(self, list_name):
		trello_list = self.get_list_by_name(list_name)
		result = []
		localhost = socket.gethostname()
		for card in self.trello_board.all_cards():
			if card.list_id == trello_list.id and localhost in card.description:
				result.append(card)
		return result
	
	def get_list_by_name(self, list_name):
		for trello_list in self.trello_board.all_lists():
			if trello_list.name == list_name:
				return trello_list
		return None

	def get_card_by_name(self, card_name):
		for card in self.trello_board.all_cards():
			if card.name == card_name:
				return card

	def update(self, flowcells):
		for flowcell in flowcells:
			card = self.get_card_by_name(flowcell.name) or self.create_card(flowcell)
			if flowcell.due_date:
				card.set_due(flowcell.due_date)
			self.move_card(card, flowcell.status)
			self.add_label(card)
			if flowcell.check_status:
				card.comment(flowcell.check_status)

	def create_card(self, flowcell):
		trello_list = self.get_list_by_name(flowcell.status)
		trello_card = trello_list.add_card(name=flowcell.name, desc=flowcell.description)
		return trello_card

	def archive_nosync_cards(self, nosync_flowcells):
		nosync_cards = self.get_cards_by_list_name(FC_STATUSES['NOSYNC'])
		nosync_flowcell_names = [flowcell.name for flowcell in nosync_flowcells]
		for card in nosync_cards:
			if card.name not in nosync_flowcell_names:
				self.move_card(card, FC_STATUSES['ARCHIVED'])

	def get_label_by_name(self, name):
		labels = self.trello_board.get_labels()
		for label in labels:
			if label.name == name:
				return label
		return None

	def add_label(self, card):
		label_name = socket.gethostname()
		label = self.get_label_by_name(label_name)
		# if label exists
		if label is not None:
			# add label if it's not on the card, otherwise do nothing
			if label.id not in card.label_ids:
				card.add_label(label)
		else:
			# if doesn't exist, create and add to the card
			color = self._next_color()
			label = self.trello_board.add_label(name=label_name, color=color)
			card.add_label(label)


	def move_card(self, card, new_list_name):
		new_list = self.get_list_by_name(new_list_name)
		card.change_list(new_list.id)


	def _next_color(self):
		labels = self.trello_board.get_labels()
		all_colors = [label.color for label in labels]
		used_colors = [label.color if label.name else '' for label in labels]

		if used_colors == all_colors:
			return all_colors[0]

		elif set(used_colors) != set(all_colors):
			for color in all_colors:
				if color not in used_colors:
					return color

		else:
			color_groups = {}
			for color in all_colors:
				color_groups[color] = all_colors.count(color)

			for color in color_groups:
				count = color_groups[color]
				if count == min(color_groups.values()):
					return color
