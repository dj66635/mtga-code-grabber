import re

# built the regex string to allow for some slack in OCR parser, will fix be fixed in postprocessing
def findCode(text):
    code_pattern = r'[A-Z0-9!?@#$%^=&]{5}[-][A-Z0-9!?@#$%^=&]{5}[-][A-Z0-9!?@#$%^=&]{5}[-][A-Z0-9!?@#$%^=&]{5}[-][A-Z0-9!?@#$%^=&]{5}'
    matches = re.findall(code_pattern, text)
    return matches


