import sublime
import sublime_plugin
import re

class SassSelectionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    settings  = self.view.settings()
    (current_row, current_row_index) = self.validate_selection()
    raw_indent = self.calculate_indent_count(self.view.substr(current_row))
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
    # Find nearest SASS selector fragment

    # Implementation placeholder
    nearest_sass_fragment = None

    # Traverse selector tree to root (i.e. no indent)
    #while (not is_root(nearest_sass_fragment))
      #current_row = get_previous_row(current_row)
      #if (is_indented_at(expected_indent_level, current_row) && is_sass_fragment(current_row))
      #  sass_fragments.push(row_at(current_row))


    # 'Compile' selector to true CSS
    #for (i = len(sass_fragments); i > 0; i--)
    #  computed_css = sass_fragments.pop();
    #  flatten_sass_syntax(computed_css);


  # Returns first selection region if it covers only one row
  def validate_selection(self):
    all_selections = self.view.sel()
    if len(all_selections) != 1:
      self.report_expiring_message('warning', 'Multiple regions selected, using first')

    current_row = self.view.line(all_selections[0])

    (begin_row, begin_col) = self.view.rowcol(current_row.begin())
    (end_row, end_col)     = self.view.rowcol(current_row.end())

    if begin_row == end_row:
      return (current_row, begin_row)
    else:
      self.report_expiring_status('error', 'Multi-row regions are not supported', 5000)
      raise Exception('Multi-row region was selected, logic for this not yet determined')

  # Returns a string containing all the leading whitespace of a row
  def calculate_indent_count(self, line):
    full_indentation = re.search('^(\s*)', line).groups()[0]

    return full_indentation

  # Gets the region for the line before the current line.
  # This works by getting the region of the point BEFORE the current line begins (i.e. the previous line)
  def get_previous_row(self, current_row):
    one_char_before = sublime.Region(current_row.begin() - 1)

    return self.view.line(one_char_before)

  # Determines if a region has no indentation (i.e. it is a 'root' selector)
  def is_root(self, row):
    return len(self.calculate_indent_count(row)) == 0

  # Quick debugging logger
  def report_expiring_status(self, status_key, status_message, timeout=3000):
    self.view.set_status(status_key, status_message)
    sublime.set_timeout(lambda: self.view.erase_status(status_key), timeout)