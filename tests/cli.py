import logging
import click

from utils.config.config import CONFIG
from tests.test_hiseqx import TestHiseqX
from tests.test_hiseq import TestHiseq
from tests.test_miseq import TestMiseq

import unittest

@click.command()
@click.option("--hiseqx", is_flag=True)
@click.option("--hiseq", is_flag=True)
@click.option("--miseq", is_flag=True)
@click.option("--all", is_flag=True)
def test_flowcells(hiseqx, hiseq, miseq, all):
	""" Run unittests with the default config file: tests/config.yaml. To change it, edit tests/test_<fc-type>.py file"""
	if not CONFIG.get('trello', ''):
		logging.error("Config file missing required entries: 'trello'")
		raise RuntimeError("Config file missing required entries: 'trello'")
	if not CONFIG.get('data_folders', ''):
		logging.error("Config file missing required entries: 'data_folders'")
		raise RuntimeError("Config file missing required entries: 'data_folders'")
	if all:
		for Test in [TestMiseq, TestHiseq, TestHiseqX]:
			suite = unittest.TestLoader().loadTestsFromTestCase(Test)
			unittest.TextTestRunner(verbosity=2).run(suite)
	else:
		if hiseqx:
			suite = unittest.TestLoader().loadTestsFromTestCase(TestHiseqX)
			unittest.TextTestRunner(verbosity=2).run(suite)
		if hiseq:
			suite = unittest.TestLoader().loadTestsFromTestCase(TestHiseq)
			unittest.TextTestRunner(verbosity=2).run(suite)
		if miseq:
			suite = unittest.TestLoader().loadTestsFromTestCase(TestMiseq)
			unittest.TextTestRunner(verbosity=2).run(suite)
