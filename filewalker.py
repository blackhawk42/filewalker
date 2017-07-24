#!/usr/bin/env python3

import shutil			# File stuff
import os, os.path		# Os and, specially, pathname manipulation
import sys
import zlib				# CRC32

import logging
import getopt

import random			# Form random names
import string

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)
#handler = logging.FileHandler('debugger.log')
#logger.addHandler(handler)

usage = "usage: {} [-r|--root=ROOT_DIR] [-o |--output=DUMP_DIR] [-a|--all] [-h|--help] [-d|--debug] [-s|--silent] EXTENSION1 [EXTENSION2 ...]".format(sys.argv[0])

def get_random_name(length=8):
	"""Random name generation, for filenames, etc."""
	chars = []
	for i in range(length):
		chars.append(random.choice(string.ascii_letters + string.digits))
	return ''.join(chars)
		

if __name__ == "__main__":
	
	possible_opts = "r:o:ahds"
	possible_opts_large = ["root=", "output=", "--all", "help", "debug", "silent"]
	
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], possible_opts, possible_opts_large)
	except getopt.GetoptError as e:
		logger.error("{}\n{}".format(str(e), usage))
		sys.exit(2)
	
	default_dest = get_random_name()
	dest = os.path.join(os.getcwd(), default_dest) # Default dest dir is a dir named randomly in the current directory
	logger.debug("Default dump dir: {}".format(default_dest))
	
	rootDir = os.getcwd() # Default root is current working directory
	
	all_files = False
	for opt, arg in opts:
		if opt in ["-o", "--output"]:
			dest = os.path.abspath(arg)
		elif opt in ["-d", "--debug"]:
			logger.setLevel(logging.DEBUG)
		elif opt in ["-s", "--silent"]:
			logger.setLevel(logging.ERROR)
		elif opt in ["-h", "--help"]:
			logger.error(usage) # Not really an error. Oh, well...
			sys.exit(0)
		elif opt in ["-a", "--all"]:
			logger.debug("Searching for all types of files")
			all_files = True
		elif opt in ["-r", "--root"]:
			rootDir = os.path.abspath(arg)
			logger.debug("root dir changed to {}".format(rootDir))
		else:
			logger.error("Unexpected options error.\n{}".format(usage))
	
	extensions = args
	if all_files == False:
		logger.debug("Extensions to search: {}".format(extensions))
	
	if len(extensions) == 0 and all_files == False:
		logger.error("There must be at least one file extension or search for all file\n{}".format(usage))
		sys.exit(1)
	
	logger.info("Using as destination: {}".format(dest))
	if not os.path.isdir(dest):
		logger.info("{} doesn't exists; creating".format(dest))
		os.mkdir(dest)
	
	logger.debug("Starting walk")
	for root, dirs, files in os.walk(rootDir):
		if root != dest:
			logger.debug("root: {}, dirs: {}, files: {}".format(root, dirs, files))
			for file in files:
				logger.debug("File found: {}. Separating".format(file))
				base, ext = os.path.splitext(file)
				if ext[1:] in extensions or all_files: 
					logger.debug("File {} recognized. Getting absolute path".format(file))
					curfile = os.path.join(root, file) # Current file
					logger.debug("Absolute path of {}: {}. Computing CRC32".format(file, curfile))
					with open(curfile, "rb") as f:
						crc = "{:8X}".format(zlib.crc32(f.read()) & 0xffffffff)
						logger.debug("CRC32: {}".format(crc))
					newname = "{}[{}]{}".format(base, crc, ext)
					logger.debug("New name: {}".format(newname))
					logger.info("Copying file from {} to {}".format(curfile, os.path.join(dest, newname)))
					shutil.copyfile(curfile, os.path.join(dest, newname))
		else:
			logger.debug("Inside dump directory, nothing done")


logger.info("Done")
