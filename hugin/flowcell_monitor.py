import os
import trello
import socket

from flowcells import Flowcell
from flowcell_status import FlowcellStatus


class FlowcellMonitor(object):

    def __init__(self, config):
        self._config = config
        # initialize None values for @property functions
        self._trello_board = None
        self._data_folders = None
        self._trello_cards = None
        self._trello_lists = None

    @property
    def config(self):
        return self._config

    @property
    def trello_board(self):
        if not self._trello_board:
            if not self.config.get('trello'):
                raise RuntimeError("'trello' must be in config file")

            config = self.config.get('trello')
            # todo check if board exist

            api_key = config.get('api_key')
            token = config.get('token')
            api_secret = config.get('api_secret')
            client = trello.TrelloClient(api_key=api_key, token=token, api_secret=api_secret)
            board_id = config.get('board_id')
            self._trello_board  = client.get_board(board_id)

        return self._trello_board

    @property
    def data_folders(self):
        if not self._data_folders:
            self._data_folders = self.config.get('data_folders')
            if self._data_folders is None:
                raise RuntimeError("'data_folders' must be in config file")
        return self._data_folders

    @property
    def trello_cards(self):
        if self._trello_cards is None:
            self._trello_cards = self.trello_board.all_cards()
        return self._trello_cards

    @property
    def trello_lists(self):
        if self._trello_lists is None:
            self._trello_lists = self.trello_board.all_lists()
        return self._trello_lists

    def update_trello_board(self):
        trello_cards = self.trello_board.all_cards()
        for card in trello_cards:
            card.delete()

        for data_folder in self.data_folders:
            # go throw subfolders
            for subfolder in os.walk(data_folder): # os.walk returns list of tuples (dirpath, dirnames, filenames)
                flowcell_path = subfolder[0]

                if flowcell_path == data_folder: # skip ./
                    continue

                status = FlowcellStatus(flowcell_path)
                # depending on the type, return instance of related class (hiseq, hiseqx, miseq, etc)
                flowcell = Flowcell.init_flowcell(status)
                # update flowcell status
                self._update_card(flowcell)


    def _get_trello_card(self, flowcell):
        for card in self.trello_cards:
            if flowcell.full_name == card.name:
                return card
        return None


    def _create_card(self, flowcell):
        trello_list = self._get_list_by_name(flowcell.list)
        if not trello_list:
            raise RuntimeError('List {} cannot be found in TrelloBoard {}'.format(flowcell.status, self.trello_board))

        trello_card = trello_list.add_card(name=flowcell.full_name, desc=flowcell.get_formatted_description())
        if flowcell.list == flowcell.status.statuses['CHECKSTATUS']:
            trello_card.comment(flowcell.status.warning)


    def _update_card(self, flowcell):
        trello_card = self._get_trello_card(flowcell) # None
        flowcell_list = self._get_list_by_name(flowcell.list)

        # if not card on trello board
        if trello_card is None:
            return self._create_card(flowcell)

        else:
            # skip aborted list
            if flowcell.list == flowcell.status.statuses['ABORTED']:
                return trello_card

            # if card is in the wrong list
            if trello_card.list_id != flowcell_list.id:
                # move card
                trello_card.delete()
                return self._create_card(flowcell)

            # if card is in the right list
            else:
                # todo: checkstatus -> taking too long?
                return trello_card

    def _get_list_by_name(self, list_name):
        for item in self.trello_lists:
            if item.name == list_name:
                return item
        return None

