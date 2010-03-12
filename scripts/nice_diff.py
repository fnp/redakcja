import difflib
import re

def read_whole(path):
	with open(path) as f:
		return f.readlines()

DIFF_RE = re.compile(r"""\x00([+^-])""" ,re.UNICODE)
NAMES = { '+': 'added', '-': 'removed', '^': 'changed' }

def diff_replace(match):
	return """<span class="diff_mark diff_mark_%s">""" %  NAMES[match.group(1)]


def filter_line(line):
	return DIFF_RE.sub(diff_replace, line).replace('\x01', '</span>')

def group(diffs):
	group_a = []
	group_b = []

	a, b, _ = diffs.next()
	group_a.append(a[1])
	group_b.append(b[1])


	for _ in range(10):
		a, b, _ = diffs.next()
		group_a.append(a[1])
		group_b.append(b[1])	

		while a[0] == '':
			a, b, _ = diffs.next()
			group_a.append(a[1])
			group_b.append(b[1])

		yield group_a[:-1], group_b[:-1]
		group_a, group_b = group_a[-1:], group_b[-1:]

def join_to_html(diffs):
	for group_a, group_b in group(diffs):
		yield """
<div class="change_block">
	<div class="old_block">%s</div>
	<div class="new_block">%s</div>
</div>""" % ( 
	'\n'.join( filter_line(line) for line in group_a ),
	'\n'.join( filter_line(line) for line in group_b ),
	)

fa = read_whole("file_a")
fb = read_whole("file_b")

print '\n'.join( repr(x) for x in  difflib._mdiff(fa, fb)  )
print "**************************"
print '\n'.join( join_to_html( difflib._mdiff(fa, fb) ) )
# print '\n'.join( repr(x) for x in group(difflib._mdiff(fa, fb)) )
