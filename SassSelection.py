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
  def get_indentation(self, line):
    full_indentation = re.search('^(\s*)', line).groups()[0]

    return full_indentation

  # Gets the region for the line before the current line.
  # @line_region - The region for the entire current row
  def get_previous_row(self, line_region):
    one_char_before = sublime.Region(line_region.begin() - 1)

    return self.view.line(one_char_before)

  # Determines if a region has no indentation (i.e. it is a 'root' selector)
  def is_root(self, row):
    return len(self.get_indentation(row)) == 0

  def is_like_sass(self, candidate):
    selector_pattern = '([#\.][\w\d\-%]+)+'

    return (re.search(selector_pattern, candidate) != None)

  def find_nearest_sass_fragment(self, region):
    inspected_line = self.view.line(region)

    if (self.is_like_sass(self.contents_of(inspected_line))):
      if (self.is_root(self.contents_of(inspected_line))):
        return self.contents_of(inspected_line)
      else:
        inspected_line = get_previous_row(inspected_line)

    while (self.is_like_sass(self.contents_of(inspected_line)) == False):
      inspected_line = self.get_previous_row(inspected_line)

    return inspected_line

  def collect_sass_fragments(self, region):
    sass_fragments = []

    lowest_fragment = self.find_nearest_sass_fragment(region)

    sass_fragments.append(lowest_fragment)

    return sass_fragments

  def contents_of(self, region):
    return self.view.substr(region)

  # Quick debugging logger
  def report_expiring_status(self, status_key, status_message, timeout=3000):
    self.view.set_status(status_key, status_message)
    sublime.set_timeout(lambda: self.view.erase_status(status_key), timeout)