# common errors
def postProcess(code):
    fixcode = code.replace(' ','-').replace('O', '0').replace('$','3')
    return fixcode

# will sometimes fix one character error...
def retryCodes(code):
    codes = []
    if '5' in code:
        codes.append(code.replace('5','S'))
    if 'S' in code:
        codes.append(code.replace('S','5'))
    if '1' in code:
        codes.append(code.replace('1','I'))
    if 'I' in code:
        codes.append(code.replace('I','1'))
    if 'B' in code:
        codes.append(code.replace('B','8'))
    if '8' in code:
        codes.append(code.replace('8','B'))
    if '6' in code:
        codes.append(code.replace('6','G'))
    if 'G' in code:
        codes.append(code.replace('G','6'))
    return codes
