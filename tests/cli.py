import logging

import click
from utils.config.config import CONFIG
from tests.test_flowcell import run_test


@click.group()
def test():
	pass
@test.command()
def test_flowcells():
	""" Run unittests"""
	if not CONFIG.get('trello', ''):
		logging.error("Config file missing required entries: 'trello'")
		raise RuntimeError("Config file missing required entries: 'trello'")
	if not CONFIG.get('data_folders', ''):
		logging.error("Config file missing required entries: 'data_folders'")
		raise RuntimeError("Config file missing required entries: 'data_folders'")
	run_test()
