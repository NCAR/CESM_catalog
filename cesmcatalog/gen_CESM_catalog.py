#!/usr/bin/env python
"""
  Goal: a script that gets pointed to a CESM case directory and generates
        an intake-esm catalog of output in the short-term archive directory

  Current state: a script that gets pointed to a CESM case directory and prints
                 some environment variables that will be necessary for above

  NOTE: this script needs to be run in the CESM postprocessing python environment,
        which is still based on python 2.7. Follow instructions at

        https://github.com/NCAR/CESM_postprocessing/wiki/cheyenne-and-DAV-quick-start-guide
"""

import os
import sys
import subprocess
import logging
import argparse

################################################################################

def _parse_args():
  """ Wrapper for argparse, returns dictionary of arguments """

  parser = argparse.ArgumentParser(description="Generate intake-esm catalog for a CESM case",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-c', '--case-root', action='store', dest='case_root', required=True,
                      help='CESM case root to generate intake-esm catalog for')

  return parser.parse_args()

################################################################################

def _find_data(case_root):
  logger = logging.getLogger(__name__)

  # 1. change directory to case_root (if it exists)
  try:
    os.chdir(case_root)
  except:
    # TODO: set up logger instead of print statements
    logger.error('%s does not exist' % case_root)
    sys.exit(1)

  # 2. Collect info on where time slice output is
  if not os.path.isfile('./xmlquery'):
    # TODO: set up logger instead of print statements
    logger.error('Can not find xmlquery in %s' % case_root)
    sys.exit(1)

  run_config = dict()
  for var in ['GET_REFCASE', 'RUN_REFCASE']:
    run_config[var] = subprocess.check_output('./xmlquery --value %s' % var, shell=True)
  DOUT_S = subprocess.check_output('./xmlquery --value DOUT_S', shell=True)
  if DOUT_S == 'TRUE':
    DOUT_S_ROOT = subprocess.check_output('./xmlquery --value DOUT_S_ROOT', shell=True)
  else:
    DOUT_S_ROOT = None

  # 3. If time series preprocess was used, pull out necessary config data
  # TODO: how do we determine if we actually generated timeseries?
  if os.path.isdir('postprocess'):
    os.chdir('postprocess')
    TIMESERIES_OUTPUT_ROOTDIR = subprocess.check_output('./pp_config --value --get TIMESERIES_OUTPUT_ROOTDIR', shell=True).rstrip()
  else:
    TIMESERIES_OUTPUT_ROOTDIR = None

  return run_config, DOUT_S_ROOT, TIMESERIES_OUTPUT_ROOTDIR

################################################################################

def gen_catalog(case_root):
  logger = logging.getLogger(__name__)

  # 1. Find where data is
  run_config, DOUT_S_ROOT, TIMESERIES_OUTPUT_ROOTDIR = _find_data(case_root)
  if (DOUT_S_ROOT is None) and (TIMESERIES_OUTPUT_ROOTDIR is None):
    logger.error('Error: can not find any data for %s' % case_root)
    sys.exit(1)

  logger.info('run_config: %s' % run_config)

  if DOUT_S_ROOT:
    # TODO: generate catalog instead of just printing this
    logger.info('DOUT_S_ROOT: %s' % DOUT_S_ROOT)

  if TIMESERIES_OUTPUT_ROOTDIR:
    # TODO: generate catalog instead of just printing this
    logger.info('TIMESERIES_OUTPUT_ROOTDIR: %s' % TIMESERIES_OUTPUT_ROOTDIR)

################################################################################

if __name__ == "__main__":
  logging.basicConfig(format='%(levelname)s (%(funcName)s): %(message)s', level=logging.DEBUG)
  args = _parse_args()
  gen_catalog(args.case_root)
