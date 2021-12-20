#!/usr/bin/env python3

#
# Databases and Management Tools
# lab3 2021-12-20
# Mykytenko Illya FPM KB-94
#

import configparser
import psycopg2
import types
import Lab
import peewee


def main() -> None:
	configfile_path, configfile_section = f"./postgres.ini.secure", f"Database"
	configfile = configparser.ConfigParser()
	configfile.read(configfile_path)
	config = {a: configfile.get(configfile_section, a) for a in configfile.options(configfile_section)}

	Lab.controller.Controller(config).start()


if __name__ == "__main__":
	# template script file, code:
	main()
	# exit(r'MAIN_RETURN_0')
