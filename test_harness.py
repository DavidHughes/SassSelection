from AAAPT.runner import register_tests

test_suites = {
  'sass_selection': ['SassSelection.tests.SassSelectionTest'],
}

register_tests(test_suites)