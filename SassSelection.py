import sublime
import sublime_plugin
import re

class SassSelectionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    settings  = self.view.settings()
    (current_row, current_row_index) = self.validate_selection()
    raw_indent = self.get_indentation(self.view.substr(current_row))
    use_spaces = settings.get('translate_tabs_to_spaces')
    indent_count = len(raw_indent)
    expected_indent_level = indent_count - 1
    sass_fragments = []

    if use_spaces:
      tab_size = settings.get('tab_size', 4)
      indent_count /= tab_size

    previous_line = self.get_previous_row(current_row)

    if (previous_line == None):
      self.handle_malformed_sass()

    self.report_expiring_status('message', 'Previous line: %s' % self.view.substr(self.view.line(previous_line)))

    is_root = self.is_root(previous_line)

    self.report_expiring_status('indent', 'This line is %sa root candidate' % ('' if is_root else 'not '))

    # TODO:
    # - Gather SASS fragments
    # - 'Compile' selector to true CSS

  # Returns first selection region if it covers only one row
  def validate_selection(self):
    all_selections = self.view.sel()
    if len(all_selections) > 1:
      self.report_expiring_status('warning', 'Multiple regions selected, using first')
    elif len(all_selections) == 0:
      raise RuntimeError("Nothing is selected")

    current_row = self.view.line(all_selections[0])

    (begin_row, begin_col) = self.view.rowcol(current_row.begin())
    (end_row, end_col)     = self.view.rowcol(current_row.end())

    if begin_row == end_row:
      return (current_row, begin_row)
    else:
      self.report_expiring_status('error', 'Multi-row regions are not supported', 5000)
      raise NotImplementedError('Multi-row region was selected, logic for this not yet determined')

  # Returns a string containing all the leading whitespace of a row
  def get_indentation(self, line_region):
    line = self.contents_of(line_region)
    full_indentation = re.search('^(\s*)', line).groups()[0]

    return full_indentation

  # Returns the amount of times the line has been "tabbed"
  def get_logical_indent(self, line_region):
    settings = self.view.settings()
    inspected_line = self.view.line(line_region)
    current_raw_indentation = self.get_indentation(inspected_line)
    use_spaces = settings.get('translate_tabs_to_spaces')

    indent_level = len(current_raw_indentation)
    if (use_spaces):
      indent_level /= settings.get('tab_size', 4)

    return indent_level

  # Gets the region for the line before the current line.
  # @line_region - The region for the entire current row
  def get_previous_row(self, line_region):
    region_start = line_region.begin()

    if (region_start > 0):
      one_char_before = sublime.Region(line_region.begin() - 1)
      return self.view.line(one_char_before)
    else:
      return None

  # Determines if a region has no indentation (i.e. it is a 'root' selector)
  def is_root(self, line_region):
    return len(self.get_indentation(line_region)) == 0

  def is_like_sass(self, candidate):
    selector_pattern = '([#\.][\w\d\-%]+)+'

    exceptions = [
      'color:',
      'background-color:',
      'background:',
      'outline-color:',
      'outline:',
      'text-shadow:',
      'box-shadow'
      ]

    for exception in exceptions:
      is_property = re.search(exception, candidate)
      if (is_property):
        return False

    return (re.search(selector_pattern, candidate) != None)

  def find_nearest_sass_fragment(self, region):
    inspected_line = self.view.line(region)
    current_indent_level = self.get_logical_indent(inspected_line)
    parent_indent_level = current_indent_level - 1

    if (self.is_root(inspected_line)):
      if (not self.is_like_sass(self.contents_of(inspected_line))):
        self.handle_malformed_sass()
      return None

    inspected_line = self.get_previous_row(inspected_line)
    while (self.get_logical_indent(inspected_line) != parent_indent_level):
      inspected_line = self.get_previous_row(inspected_line)

    if (inspected_line == None or self.is_like_sass(self.contents_of(inspected_line)) == False):
      self.handle_malformed_sass()
      return None

    return inspected_line

  def collect_sass_fragments(self, selected_region):
    sass_fragments = []

    if (self.is_like_sass(self.contents_of(selected_region))):
      sass_fragments.append(self.contents_of(selected_region))

    nearest_fragment_region = self.find_nearest_sass_fragment(selected_region)

    while (nearest_fragment_region != None):
      sass_fragments.append(self.contents_of(nearest_fragment_region))
      nearest_fragment_region = self.find_nearest_sass_fragment(nearest_fragment_region)


    return sass_fragments

  def contents_of(self, region):
    return self.view.substr(region)

  def handle_malformed_sass(self):
    raise RuntimeError("Malformed SASS is in place, attributes are being declared where they shouldn't be")

  # Quick debugging logger
  def report_expiring_status(self, status_key, status_message, timeout=3000):
    self.view.set_status(status_key, status_message)
    sublime.set_timeout(lambda: self.view.erase_status(status_key), timeout)