
"""Author: Mark Hanegraaff -- 2022
Pytest driver. All unit tests are run from this script.
"""
import unittest
import logging
from test.test_parsers_email import TestEmailMessage



logging.basicConfig(level=logging.ERROR,
                    format='[%(levelname)s] - %(message)s')

if __name__ == '__main__':
    unittest.main()