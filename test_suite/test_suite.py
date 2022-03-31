__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

import unittest

import infrastructure.test_infrastructure as test_infrastructure
import highcliff.actions.test_actions as test_actions
import ai.test_ai as test_ai
import highcliff.exampleactions.test_exampleactions as test_example_actions
import examples.test_examples as test_examples

import highcliff.airflow.test_airflow as test_airflow


# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add general tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_infrastructure))
suite.addTests(loader.loadTestsFromModule(test_actions))
suite.addTests(loader.loadTestsFromModule(test_ai))
suite.addTests(loader.loadTestsFromModule(test_example_actions))
suite.addTests(loader.loadTestsFromModule(test_examples))

# add specific domain tests to the suite
suite.addTests(loader.loadTestsFromModule(test_airflow))

# initialize runner, pass runner the suite, run the tests
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
