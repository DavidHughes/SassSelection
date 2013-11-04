import unittest

from sublime         import Region
from AAAPT.utils     import BufferTest
from ..SassSelection import SassSelectionCommand

class Test_SassSelectionCommand(BufferTest):
  def test_get_indentation(self):
    indent = SassSelectionCommand.get_indentation(self, 'This is not indented')
    self.assertEqual(len(indent), 0)

  def test_get_previous_row(self):
    expected_previous_row = 'Line 1'
    region_begin = len(expected_previous_row)
    full_text = expected_previous_row + '\nThe second line'
    self.set_text(full_text)
    region = Region(len(expected_previous_row), len(full_text))

    previous_row_region = SassSelectionCommand.get_previous_row(self, region)
    actual_previous_row = full_text[previous_row_region.begin():previous_row_region.end()]
    self.assertEqual(actual_previous_row, expected_previous_row)
