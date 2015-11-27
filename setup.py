#!/usr/bin/env python

from setuptools import setup, find_packages
import os


try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

try:
    with open("dependency_links.txt", "r") as f:
        dependency_links = [x.strip() for x in f.readlines()]
except IOError:
    dependency_links = []

setup(name = "hugin",
      version = "0.1",
      author = "Kate S.",
      author_email = "ekaterina.stepanova@scilifelab.se",
      description = "A system for monitoring sequencing and analysis status at SciLifeLab",
      license = "MIT",
      entry_points={
            'console_scripts': ['hugin = cli:cli'],
            'hugin.subcommands': [
                'monitor_flowcells=monitor_flowcells.cli:monitor_flowcells',
                # 'server_status = taca.server_status.cli:server_status',
            ]
      },
      install_requires = install_requires,
      dependency_links = dependency_links,
      packages=find_packages(exclude=['tests']),
      )

os.system("git rev-parse --short --verify HEAD > ~/.hugin_version")
