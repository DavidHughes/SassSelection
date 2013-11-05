import unittest

from sublime         import Region
from AAAPT.utils     import BufferTest
from ..SassSelection import SassSelectionCommand

class Test_SassSelectionCommand(BufferTest):
  text = ['#selector', '  width: 100%', '  &.disabled', '    color: #666666']
  compiled_css = ['#selector', '#selector.disabled']

  # TODO: Sort out inheritance/construction of SassSelectionCommand so this is redundant
  report_expiring_status = (lambda self, status, msg, timeout=3000: "OK")
  is_like_sass     = SassSelectionCommand.is_like_sass
  contents_of      = SassSelectionCommand.contents_of
  get_previous_row = SassSelectionCommand.get_previous_row
  is_root          = SassSelectionCommand.is_root
  get_indentation  = SassSelectionCommand.get_indentation

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

  # Tests against multiple selected regions.
  # Expected: function uses first region
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

  # Tests against a single multiple row selection region.
  # Expected: NotImplementedError
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

  def test_is_like_sass_actual_sass(self):
    copy = self.text[0]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertTrue(is_like_sass)

  def test_is_like_sass_attr_declaration(self):
    copy = self.text[1]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertFalse(is_like_sass)

  def test_validate_selection_no_sel(self):
    self.set_text('\n'.join(self.text))

    exception_thrown = False
    try:
      SassSelectionCommand.validate_selection(self)
    except RuntimeError:
      exception_thrown = True

    self.assertTrue(exception_thrown, 'Expected a RuntimeError')

  #  The test_find_sass_fragments_X test methods all test the to-be-implemented find_sass_fragments methods
  #  They collectively will cover the four basic situations I've thought of:
  #   | #id              <- _base
  #   |   attr: value    <- _base_declaration
  #   |   .class         <- _nested
  #   |     attr: value  <- _nested_declaration

  def test_find_nearest_sass_fragment_from_root_selector(self):
    self.set_text('\n'.join(self.text))
    region = self.R(0, 0)
    self.add_sel(region)

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, region)
    self.assertEqual(actual_nearest_sass, self.text[0])

  def test_find_nearest_sass_fragment_from_attr_declaration(self):
    self.set_text('\n'.join(self.text))
    region = self.R(1, 0)
    self.add_sel(region)

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, region)
    self.assertEqual(actual_nearest_sass, self.text[0])

  def test_find_nearest_sass_fragment_from_nested_selector(self):
    self.set_text('\n'.join(self.text))
    region = self.R(2, 0)
    self.add_sel(region)

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, region)
    self.assertEqual(actual_nearest_sass, self.text[0])

  def test_find_sass_fragments_base(self):
    self.set_text('\n'.join(self.text))
    region = self.R(0, 0)
    self.add_sel(region)

    sass_fragments = SassSelectionCommand.find_sass_fragments(self)
    self.assertEqual(len(sass_fragments), 1)
    self.assertEqual(sass_fragmnets[0], self.text[0])

  def test_find_sass_fragments_base_declaration(self):
    self.set_text('\n'.join(self.text))
    raise NotImplementedError

  def test_find_sass_fragments_nested(self):
    self.set_text('\n'.join(self.text))
    raise NotImplementedError

  def test_find_sass_fragments_nested_declaration(self):
    self.set_text('\n'.join(self.text))
    raise NotImplementedError
