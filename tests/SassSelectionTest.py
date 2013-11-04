import unittest

from AAAPT.utils   import BufferTest
from ..SassSelection import SassSelectionCommand

class Test_SassSelectionCommand(BufferTest):
  def test_calculate_indent_count(self):
    indent = SassSelectionCommand.calculate_indent_count(self, 'This is not indented')
    self.assertEqual(len(indent), 0)