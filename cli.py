# -*- coding: utf-8 -*-
import logging
import os

from pkg_resources import iter_entry_points

import click
from utils import log
from utils.config import config as conf


logger = logging.getLogger(__name__)

# @click.group()
# def monitor_flowcells():
# 	"""Monitor flowcell statuses and display the flowcells on the Trello board"""
# 	if not conf.get('data_folders', ''):
# 		logging.error("Configuration missing required entries: data_folders")
# 		raise RuntimeError("Configuration missing required entries: data_folders")

# @monitor_flowcells.command()
# def update():
# 	pass

# @monitor_flowcells.command()

# def test():
# 	pass


# @click.group()
# def server_status():
# 	""" Monitor server status """
# 	if not CONFIG.get('server_status', ''):
# 		raise RuntimeError("Configuration missing required entries: server_status")


# # server status subcommands
# @server_status.command()
# @click.option('--gdocs', is_flag=True, help="Update the google docs")
# @click.option('--statusdb', is_flag=True, help="Update the statusdb")
# @click.option('--credentials', type=click.Path(exists=True), default=os.path.join(os.environ.get('HOME'), '.taca', 'gdocs_credentials.json'),
# 				 help='Path to google credentials file')
# def nases(credentials, gdocs, statusdb):
# 	""" Checks the available space on all the nases
# 	"""
# 	disk_space = status.get_nases_disk_space()

# 	import pdb
# 	pdb.set_trace()

# 	if gdocs:
# 		status.update_google_docs(disk_space, credentials)
# 	if statusdb:
# 		status.update_status_db(disk_space)

# #  must be run on uppmax, as no passwordless ssh to uppmax servers
# @server_status.command()
# @click.option('--disk-quota', is_flag=True, help="Check the available space on the disks")
# @click.option('--cpu-hours', is_flag=True, help="Check the usage of CPU hours")
# def uppmax(disk_quota, cpu_hours):
# 	"""
# 	Checks the quotas and cpu hours on the uppmax servers
# 	"""
# 	merged_results = {}
# 	if disk_quota:
# 		disk_quota_data = status.get_uppmax_quotas()
# 		merged_results.update(disk_quota_data)
# 	if cpu_hours:
# 		cpu_hours_data = status.get_uppmax_cpu_hours()
# 		merged_results.update(cpu_hours_data)
# 	status.update_status_db(merged_results)





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
	ctx.obj = {}

	config = conf.load_yaml_config(config_file)

	log_file = config.get('log', {}).get('file', None)
	if log_file:
		log.init_logger_file(log_file, log_level)

	logger.debug('starting up CLI')


#Add subcommands dynamically to the CLI
for entry_point in iter_entry_points('hugin.subcommands'):
	cli.add_command(entry_point.load())
