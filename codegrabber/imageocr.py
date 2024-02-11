import pytesseract
import coderegex
from constants import HORIZONTAL_PSM, VERTICAL_PSM
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

pytesseract.pytesseract.tesseract_cmd = config['Tesseract']['tesseract_cmd']
scan_timeout = 2 # time to scan an image, RuntimeError if it cannot do it in time

def parseImage(img, debug=0):
    if debug >= 2: display(img.resize(int(0.2*s) for s in img.size)) 
    try:
        osd = pytesseract.image_to_osd(img, output_type='dict')
        img = img.rotate(osd['orientation'], expand=True) # an educated guess...
    except RuntimeError:
        pass
    
    # Rotation
    w, h = img.size
    if w > h: 
        customPsm = HORIZONTAL_PSM
    else:
        customPsm = VERTICAL_PSM
    
    ocr_text = ''
    
    try:
        ocr_text = pytesseract.image_to_string(img, config=customPsm, timeout=scan_timeout)
    except RuntimeError as error:
        if str(error) != 'Tesseract process timeout': print(str(error))
        
    if debug >= 3: print(ocr_text)
    matches = coderegex.findCode(ocr_text)
    return matches