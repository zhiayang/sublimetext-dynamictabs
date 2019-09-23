import sublime
import sublime_plugin
import math

from functools import reduce

class DynamicTabCommand(sublime_plugin.TextCommand):
	def get_first_whitespace(self, line):
		for i in range(0, len(line)):
			if line[i] != '\t' and line[i] != ' ':
				return i
		return -1

	def get_first_whitespace_in_region(self, v, region):
		line = v.substr(v.line(region))
		return self.get_first_whitespace(line)

	def run(self, edit):
		v           = self.view
		tabSize     = v.settings().get("tab_size")
		usingSpaces = v.settings().get("translate_tabs_to_spaces")

		for s in v.sel():
			wasEmpty = True
			if not s.empty():
				wasEmpty = False
				v.erase(edit, s)

			thisSel  = v.rowcol(s.begin())[1]
			thisLine = v.substr(v.line(s))
			firstWS  = self.get_first_whitespace_in_region(v, s)

			if firstWS != -1 and thisSel > firstWS:
				# ok... we need to calculate the next tabstop.
				# copied from https://github.com/zhiayang/vscode-tabindentspacealign/blob/master/src/extension.ts#L102
				# ie myself

				cursor = 0
				for i in range(0, thisSel):
					cursor += ((cursor % tabSize) if thisLine[i] == '\t' else 1)

				finalpos = math.ceil((cursor+1) / tabSize) * tabSize;
				v.insert(edit, s.begin(), (" " * (finalpos - cursor)))

			else:
				mult = 1
				if wasEmpty and v.rowcol(s.begin())[0] > 0:
					prevLine = v.substr(v.line(v.text_point(v.rowcol(s.begin())[0] - 1, 0)))
					ws = self.get_first_whitespace(prevLine)
					if thisSel < ws and ws != -1:
						mult = (ws / tabSize) if usingSpaces else ws
						if prevLine[-1] in ("{", ":", ","):
							mult += 1

				if usingSpaces:
					v.insert(edit, s.begin(), " " * tabSize * mult)
				else:
					v.insert(edit, s.begin(), "\t" * mult)




