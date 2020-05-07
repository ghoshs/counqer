"""
function to clean text snippets containing undefined separators.
currently only deals wth double dash separator, or dash separator which SpaCy can't handle
input: text
output: text
"""
def clean_text(text):
	new_text = ''
	prev_char = None
	for idx, char in enumerate(text):
		if idx == 0:
			new_text += char
			prev_char = char
			continue
		if char == '-' and prev_char not in [char, ' '] and idx < len(text)-1 and (text[idx+1] in [char, ' ']):
			new_text += ' ' + char 
			prev_char = char
		else:
			new_text += char
			prev_char = char
	return new_text