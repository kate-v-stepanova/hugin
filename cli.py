# -*- coding: utf-8 -*-
import logging
import os

from pkg_resources import iter_entry_points

import click
from utils import log
from utils.config import config as conf


logger = logging.getLogger(__name__)

@click.group()
# Priority for the configuration file is: environment variable > -c option > default
@click.option('-c', '--config-file',
			  default=os.path.join(os.environ['HOME'], '.hugin/config.yaml'),
			  envvar='HUGIN_CONFIG',
			  type=click.File('r'),
			  help='Path to hugin configuration file')
@click.option('-l', '--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='ERROR',
			  help='Level of the logging')
@click.pass_context
def cli(ctx, config_file, log_level):
	""" Tool to monitor flowcell statuses and display the flowcells on the Trello board """

	config = conf.load_yaml_config(config_file)
	config.update({'config_path': config_file})

	log_file = config.get('log', {}).get('file', None)
	if log_file:
		log.init_logger_file(log_file, log_level)

	logger.debug('starting up CLI')


#Add subcommands dynamically to the CLI
for entry_point in iter_entry_points('hugin.subcommands'):
	cli.add_command(entry_point.load())
