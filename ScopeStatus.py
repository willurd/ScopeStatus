import sublime, sublime_plugin

SETTING = "show_current_scope_enabled"
STATUS_KEY = "ScopeStatus"
SETTINGS_CALLBACK_KEY = "ScopeStatus"
LEFT_DELIMETER = "(Scope: "
RIGHT_DELIMETER = ")"

class ScopeStatus(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		self.update(view)

	def on_activated(self, view):
		view.settings().add_on_change(SETTINGS_CALLBACK_KEY, lambda: self.update(view))

	def on_deactivated(self, view):
		view.settings().clear_on_change(SETTINGS_CALLBACK_KEY)

	def update(self, view):
		if not view.settings().get(SETTING) or not self.set_status(view):
			self.clear_status(view)

	def set_status(self, view):
		selections = view.sel()

		if len(selections) != 1:
			# Too many (or too few) cursors.
			return False

		selection = selections[0]
		# 'b' is the last point that was entered by the cursor. This
		# is here in the case of a selection, so we display the scope
		# of the last point navigated to, and not always the start of
		# the range.
		scope_text = view.scope_name(selection.b)

		if len(scope_text) == 0:
			# There is no scope at the cursor location. (Is this
			# even possible?)
			return False

		status_text = filter(lambda s: len(s) > 0, scope_text.split(" "))
		view.set_status(STATUS_KEY, LEFT_DELIMETER + ", ".join(status_text) + RIGHT_DELIMETER)

		return True

	def clear_status(self, view):
		view.erase_status(STATUS_KEY)
		self.is_status_set = False

class ScopeSettingCommand(sublime_plugin.WindowCommand):
	"""
	A base class for commands that work with the setting that
	enables/disables the display of the scope in the status bar.
	"""
	def is_enabled(self):
		return True

	def view(self):
		return self.window.active_view()

	def is_on(self):
		return self.view().settings().get(SETTING)

class ToggleScopeInStatusBarCommand(ScopeSettingCommand):
	def run(self, **kwargs):
		self.toggle_scope_in_status_bar()

	def toggle_scope_in_status_bar(self):
		self.view().run_command("toggle_setting", {"setting": SETTING})

	def is_checked(self):
		return self.is_on()

class ShowScopeInStatusBarCommand(ScopeSettingCommand):
	def run(self, **kwargs):
		self.show_scope_in_status_bar()

	def is_enabled(self):
		return not self.is_on()

	def show_scope_in_status_bar(self):
		self.view().settings().set(SETTING, True)

class HideScopeInStatusBarCommand(ScopeSettingCommand):
	def run(self, **kwargs):
		self.hide_scope_in_status_bar()

	def is_enabled(self):
		return self.is_on()

	def hide_scope_in_status_bar(self):
		self.view().settings().set(SETTING, False)
