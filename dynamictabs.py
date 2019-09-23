import sublime
import sublime_plugin
import math

from functools import reduce

class DynamicTabCommand(sublime_plugin.TextCommand):
	def get_first_whitespace(self, edit, region):
		return next(i for i, j in enumerate(self.view.substr(self.view.line(region))) if j.strip())

	def run(self, edit):
		v = self.view
		for s in v.sel():
			if not s.empty():
				v.erase(edit, s)

			firstWS  = self.get_first_whitespace(edit, s)
			thisSel  = v.rowcol(s.begin())[1]
			thisLine = v.substr(v.line(s))
			tabSize  = v.settings().get("tab_size")

			if thisSel > firstWS:
				# ok... we need to calculate the next tabstop.
				# copied from https://github.com/zhiayang/vscode-tabindentspacealign/blob/master/src/extension.ts#L102
				# ie myself

				cursor = 0
				for i in range(0, thisSel):
					cursor += ((cursor % tabSize) if thisLine[i] == '\t' else 1)

				finalpos = math.ceil((thisSel + 1) / tabSize) * tabSize;
				v.insert(edit, s.begin(), (" " * (finalpos - thisSel)))

			else:
				if v.settings().get("translate_tabs_to_spaces"):
					v.insert(edit, s.begin(), " " * tabSize)
				else:
					v.insert(edit, s.begin(), "\t")




