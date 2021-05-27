import sublime
import sublime_plugin
import math

from functools import reduce

class DynamicTabCommand(sublime_plugin.TextCommand):
	def get_first_non_whitespace(self, line):
		for i in range(0, len(line)):
			if line[i] != '\t' and line[i] != ' ':
				return i
		return -1

	def get_first_non_whitespace_in_region(self, v, region):
		line = v.substr(v.line(region))
		return self.get_first_non_whitespace(line)

	def count_tabs(self, line):
		ret = 0
		for i in range(0, len(line)):
			if line[i] == '\t':
				ret += 1
			else:
				break
		return ret

	def run(self, edit):
		v           = self.view
		tabSize     = v.settings().get("tab_size")
		usingSpaces = v.settings().get("translate_tabs_to_spaces")

		# move this out: we only want to do extra indentation for the first
		# cursor! if not we'll end up with cascading things when we tab once.
		selIdx = 0
		mult = 1
		for s in v.sel():
			selIdx += 1

			wasEmpty = True
			if not s.empty():
				wasEmpty = False
				v.erase(edit, s)

			thisSel  = v.rowcol(s.begin())[1]
			thisLine = v.substr(v.line(s))
			firstWS  = self.get_first_non_whitespace_in_region(v, s)

			print("firstWS = {}".format(firstWS))
			print("thisSel = {}".format(thisSel))

			if firstWS != -1 and thisSel > firstWS:
				# ok... we need to calculate the next tabstop.
				# copied from https://github.com/zhiayang/vscode-tabindentspacealign/blob/master/src/extension.ts#L102
				# ie myself

				cursor = 0
				for i in range(0, thisSel):
					cursor += ((cursor % tabSize) if thisLine[i] == '\t' else 1)

				finalpos = math.ceil((cursor + 1) / tabSize) * tabSize;
				v.insert(edit, s.begin(), (" " * (finalpos - cursor)))

			else:
				if selIdx == 1:
					if wasEmpty and v.rowcol(s.begin())[0] > 0:
						prevLine = ""
						(tries, maxTries) = (0, 3)

						while tries < maxTries and len(prevLine) == 0:
							prevLine = v.substr(v.line(v.text_point(v.rowcol(s.begin())[0] - (tries + 1), 0)))
							tries += 1

						ws = self.get_first_non_whitespace(prevLine)
						if thisSel < ws and ws != -1:
							# we need to count the number of *TABS*
							if not usingSpaces:
								mult = self.count_tabs(prevLine)
							else:
								mult = (ws // tabSize)      # foo

							if prevLine[-1] in ("{", ":", ","):
								mult += 1

				if usingSpaces:
					v.insert(edit, s.begin(), " " * tabSize * mult)
				else:
					v.insert(edit, s.begin(), "\t" * mult)




