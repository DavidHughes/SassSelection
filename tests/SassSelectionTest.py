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
  get_logical_indent = SassSelectionCommand.get_logical_indent
  find_nearest_sass_fragment = SassSelectionCommand.find_nearest_sass_fragment
  handle_malformed_sass = SassSelectionCommand.handle_malformed_sass

  def test_get_indentation(self):
    regions = self.initialise_with_rows([0])

    indent = SassSelectionCommand.get_indentation(self, regions[0])
    self.assertEqual(len(indent), 0)

  def test_is_root(self):
    regions = self.initialise_with_rows([0])

    is_root = SassSelectionCommand.is_root(self, regions[0])
    self.assertTrue(is_root)

  def test_is_root_indented(self):
    regions = self.initialise_with_rows([1])

    is_root = SassSelectionCommand.is_root(self, regions[0])
    self.assertFalse(is_root)

  def test_get_previous_row(self):
    expected_previous_row = self.text[0]
    region_begin = len(expected_previous_row)
    full_text = expected_previous_row + '\n' + self.text[1]
    self.set_text(full_text)
    region = Region(len(expected_previous_row), len(full_text))

    previous_row_region = SassSelectionCommand.get_previous_row(self, region)
    actual_previous_row = full_text[previous_row_region.begin():previous_row_region.end()]
    self.assertEqual(actual_previous_row, expected_previous_row)

  def test_get_previous_row_line_two(self):
    selected_row = 2
    regions = self.initialise_with_rows([selected_row])

    previous_row_region = SassSelectionCommand.get_previous_row(self, regions[0])
    self.assertEqual(self.contents_of(previous_row_region), self.text[selected_row - 1])

  # Tests against a simple one-point selection on the first row
  def test_validate_selection_basic(self):
    begin = 0
    regions = self.initialise_with_rows([begin])

    expected_row_region = Region(0, len(self.text[0]))
    expected_row_index = 0
    (actual_row_region, actual_row_index) = SassSelectionCommand.validate_selection(self)
    self.assertEqual(actual_row_region, expected_row_region)
    self.assertEqual(actual_row_index,  expected_row_index)

  # Tests against multiple selected regions.
  # Expected: function uses first region
  def test_validate_selection_multiregion(self):
    self.initialise_with_rows([0, 1])

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

  def test_validate_selection_no_sel(self):
    self.set_text('\n'.join(self.text))

    exception_thrown = False
    try:
      SassSelectionCommand.validate_selection(self)
    except RuntimeError:
      exception_thrown = True

    self.assertTrue(exception_thrown, 'Expected a RuntimeError')

  def test_is_like_sass_simple_id(self):
    copy = self.text[0]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertTrue(is_like_sass)

  def test_is_like_sass_simple_class(self):
    copy = self.text[2]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertTrue(is_like_sass)

  def test_is_like_sass_attr_declaration(self):
    copy = self.text[1]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertFalse(is_like_sass)

  def test_is_like_sass_hexcode_in_property(self):
    copy = self.text[3]

    is_like_sass = SassSelectionCommand.is_like_sass(self, copy)
    self.assertFalse(is_like_sass)

  #   | #id              <- _base
  #   |   attr: value    <- _base_declaration
  #   |   .class         <- _nested
  #   |     attr: value  <- _nested_declaration

  def test_find_nearest_sass_fragment_from_root_selector(self):
    begin = 0
    regions = self.initialise_with_rows([begin])

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, regions[0])
    self.assertIsNone(actual_nearest_sass)

  def test_find_nearest_sass_fragment_from_attr_declaration(self):
    begin = 1
    regions = self.initialise_with_rows([begin])

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, regions[0])
    self.assertEqual(self.contents_of(actual_nearest_sass), self.text[0])

  def test_find_nearest_sass_fragment_from_nested_selector(self):
    begin = 2
    regions = self.initialise_with_rows([begin])

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, regions[0])
    self.assertEqual(self.contents_of(actual_nearest_sass), self.text[0])

  def test_find_nearest_sass_fragment_from_nested_attr_declaration(self):
    begin = 3
    regions = self.initialise_with_rows([begin])

    actual_nearest_sass = SassSelectionCommand.find_nearest_sass_fragment(self, regions[0])
    self.assertEqual(self.contents_of(actual_nearest_sass), self.text[2])

  def test_collect_sass_fragments_base(self):
    begin = 0
    regions = self.initialise_with_rows([begin])

    sass_fragments = SassSelectionCommand.collect_sass_fragments(self, regions[0])
    self.assertEqual(len(sass_fragments), 1)
    self.assertEqual(sass_fragments[0], self.text[0])

  def test_collect_sass_fragments_base_declaration(self):
    begin = 1
    regions = self.initialise_with_rows([begin])

    sass_fragments = SassSelectionCommand.collect_sass_fragments(self, regions[0])
    self.assertEqual(len(sass_fragments), 1)
    self.assertEqual(sass_fragments[0].strip(), self.text[0].strip())

  def test_collect_sass_fragments_nested(self):
    begin = 2
    regions = self.initialise_with_rows([begin])

    sass_fragments = SassSelectionCommand.collect_sass_fragments(self, regions[0])
    print(sass_fragments)
    self.assertEqual(len(sass_fragments), 2)
    self.assertEqual(sass_fragments[0].strip(), self.text[2].strip())
    self.assertEqual(sass_fragments[1].strip(), self.text[0].strip())

  def test_collect_sass_fragments_nested_declaration(self):
    begin = 3
    regions = self.initialise_with_rows([begin])

    sass_fragments = SassSelectionCommand.collect_sass_fragments(self, regions[0])
    self.assertEqual(len(sass_fragments), 2)
    self.assertEqual(sass_fragments[0].strip(), self.text[2].strip())
    self.assertEqual(sass_fragments[1].strip(), self.text[0].strip())

  # Utility methods

  def initialise(self):
    self.set_text('\n'.join(self.text))

  def initialise_with_rows(self, row_numbers):
    self.initialise()
    regions = []

    for row in row_numbers:
      region = self.calc_region_for_line(row)
      regions.append(region)
      self.add_sel(region)

    return regions

  def calc_region_for_line(self, row):
    point = self.view.text_point(row, 0)
    return self.view.line(point)