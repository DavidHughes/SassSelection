import sublime, sublime_plugin

class SassSelectionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = self.validate_selection()

    # TODO:
    # Find nearest SASS selector fragment
    # Traverse selector tree to root (i.e. no indent)
    # 'Compile' selector to true CSS

    self.report_expiring_message('message', 'Found: %s' % (self.view.substr(selection)))

  # Returns first selection region if it covers only one row
  def validate_selection(self):
    all_selections = self.view.sel()
    if len(all_selections) != 1:
      self.report_expiring_message('warning', 'Multiple regions selected, using first')

    first_region = all_selections[0]

    (begin_row, begin_col) = self.view.rowcol(first_region.begin())
    (end_row, end_col)     = self.view.rowcol(first_region.end())

    if begin_row == end_row:
      return first_region
    else:
      self.report_expiring_message('error', 'Multi-row regions are not supported', 5000)
      raise Exception('Multi-row region was selected, logic for this not yet determined')


  def report_expiring_message(self, status_key, status_message, timeout=3000):
    self.view.set_status(status_key, status_message)
    sublime.set_timeout(lambda: self.view.erase_status(status_key), timeout)