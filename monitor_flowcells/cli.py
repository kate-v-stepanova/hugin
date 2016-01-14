import click
import logging

from monitor_flowcells.flowcell_monitor import FlowcellMonitor
from utils.config.config import CONFIG

# @click.group()
@click.command()
def monitor_flowcells():
	""" Collect information from the filesystem and update the trello board"""
	if not CONFIG.get('trello', ''):
		logging.error("Config file missing required entries: 'trello'")
		raise RuntimeError("Config file missing required entries: 'trello'")
	if not CONFIG.get('data_folders', ''):
		logging.error("Config file missing required entries: 'data_folders'")
		raise RuntimeError("Config file missing required entries: 'data_folders'")

	flowcell_monitor = FlowcellMonitor(CONFIG)
	flowcell_monitor.update_trello_board()