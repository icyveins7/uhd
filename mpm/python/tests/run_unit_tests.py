#
# Copyright 2019 Ettus Research, a National Instruments Brand
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""
USRP MPM Python Unit testing framework
"""

import unittest
import sys
import argparse
from compatnum_tests import TestCompatNum
from sys_utils_tests import TestNet
from mpm_utils_tests import TestMpmUtils
from eeprom_tests import TestEeprom
from usrp_mpm import __simulated__

import importlib.util
if importlib.util.find_spec("xmlrunner"):
    from xmlrunner import XMLTestRunner

TESTS = {
    '__all__': {
        TestNet,
        TestMpmUtils,
        TestEeprom,
        TestCompatNum,
    },
    'n3xx': set(),
    'x4xx': set()
}

if not __simulated__:
    from components_tests import TestZynqComponents
    TESTS['x4xx'].update({
        TestZynqComponents
    })

def parse_args():
    """Parse arguments when running this as a script"""
    parser_help = 'Run MPM Python unittests'
    parser = argparse.ArgumentParser(description=parser_help)
    parser.add_argument('-x', '--xml', dest='xml', action='store_true', default=False,
                        help='Generate XML report (only if module xmlrunner is available)')
    parser.add_argument('device_name', help="the device name for device specific tests",
                        default='', nargs='?')
    return parser.parse_args()

def get_test_suite(device_name=''):
    """
    Gets a test suite (collection of test cases) which is relevant for
    the specified device.
    """
    # A collection of test suites, generated by test loaders, which will
    # be later combined
    test_suite_list = []
    test_loader = unittest.TestLoader()

    # Combine generic and device specific tests
    test_cases = TESTS.get('__all__') | TESTS.get(device_name, set())
    for case in test_cases:
        new_suite = test_loader.loadTestsFromTestCase(case)
        for test in new_suite:
            # Set up test case class for a specific device.
            # Each test uses a different test case instance.
            if (hasattr(test, 'set_device_name')) and (device_name != ''):
                test.set_device_name(device_name)
        test_suite_list.append(new_suite)

    # Individual test suites are combined into a master test suite
    test_suite = unittest.TestSuite(test_suite_list)
    return test_suite

def run_tests(device_name='', use_xmlrunner=False):
    """
    Executes the unit tests specified by the test suite.
    This should be called from CMake.
    """
    test_result = unittest.TestResult()
    if use_xmlrunner and 'XMLTestRunner' in globals():
        test_runner = XMLTestRunner(verbosity=2)
    else:
        test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(get_test_suite(device_name))
    return test_result

def main():
    args = parse_args()

    if not run_tests(args.device_name, use_xmlrunner=args.xml).wasSuccessful():
        sys.exit(-1)

if __name__ == "__main__":
    main()
