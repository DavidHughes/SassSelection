import unittest

from sublime         import Region
from AAAPT.utils     import BufferTest
from ..SassSelection import SassSelectionCommand

class Test_SassSelectionCommand(BufferTest):
  text = ['Line 1', '  The second line', ' I can\'t just sit here typing this all day']
  report_expiring_status = (lambda self, status, msg, timeout=3000: "OK")

  def test_get_indentation(self):
    indent = SassSelectionCommand.get_indentation(self, self.text[0])
    self.assertEqual(len(indent), 0)

  def test_get_previous_row(self):
    expected_previous_row = self.text[0]
    region_begin = len(expected_previous_row)
    full_text = expected_previous_row + '\n' + self.text[1]
    self.set_text(full_text)
    region = Region(len(expected_previous_row), len(full_text))

    previous_row_region = SassSelectionCommand.get_previous_row(self, region)
    actual_previous_row = full_text[previous_row_region.begin():previous_row_region.end()]
    self.assertEqual(actual_previous_row, expected_previous_row)

  # Tests against a simple one-point selection on the first row
  def test_validate_selection_basic(self):
    self.set_text('\n'.join(self.text))
    region = self.R(0, 0)
    self.add_sel(region)
    expected_row_region = Region(0, len(self.text[0]))
    expected_row_index = 0
    (actual_row_region, actual_row_index) = SassSelectionCommand.validate_selection(self)
    self.assertEqual(actual_row_region, expected_row_region)
    self.assertEqual(actual_row_index,  expected_row_index)

  # Tests against multiple selected regions. Expected: function uses first region
  def test_validate_selection_multiregion(self):
    self.set_text('\n'.join(self.text))
    regions = [self.R(0, 0), self.R(1, 0)]

    for region in regions:
      self.add_sel(region)

    expected_row_region = Region(0, len(self.text[0]))
    expected_row_index = 0
    (actual_row_region, actual_row_index) = SassSelectionCommand.validate_selection(self)
    self.assertEqual(actual_row_region, expected_row_region)
    self.assertEqual(actual_row_index,  expected_row_index)

  # Tests against a single multiple row selection region. Expected: NotImplementedError
  def test_validate_selection_multirow(self):
    self.set_text('\n'.join(self.text))
    region = self.R((0, 0), (1, 0))
    self.add_sel(region)

    exception_thrown = False
    try:
      SassSelectionCommand.validate_selection(self)
    except NotImplementedError:
      exception_thrown = True

    self.assertTrue(exception_thrown, 'Expected a NotImplementedError')

  def test_validate_selection_no_sel(self):
    self.set_text('\n'.join(self.text))

    exception_thrown = False
    try:
      SassSelectionCommand.validate_selection(self)
    except RuntimeError:
      exception_thrown = True

    self.assertTrue(exception_thrown, 'Expected a RuntimeError')
