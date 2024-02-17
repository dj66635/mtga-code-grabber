import PIL
import io
import multiprocessing
import imagepreprocessor
import imageocr
import coderegex
import codepostprocessor
import mtgaapi
from constants import IMG, TXT, LOG_FILE
import configparser
import logging

config = configparser.ConfigParser()
config.read('config.ini')

workers = int(config['Tesseract']['workers']) # number of ocr threads, more than 2/3 doesnt seem to be worth it

def process(source, title, url, content, contentType):
    print('-' * 100)
    headline = f'New {source} Post - Title: {shorten(title)} - Content Type: {contentType}'
    print(headline)
    
    if contentType == IMG:
        img = PIL.Image.open(io.BytesIO(content))
        print('  Preprocessing image...')
        imgs = imagepreprocessor.preProcess(img)
        print('  OCR-processing image...')
        codes = set(parallelOCRProcessing(imgs, workers))
        print('  Looking for codes...')
        codes = set([codepostprocessor.postProcess(code) for code in codes])
                    
    elif contentType == TXT:
        print('  Looking for codes...')
        codes = coderegex.findCode(content)
        codes = [codepostprocessor.postProcess(code) for code in codes]
    else:
        print('  Unsupported content type')    
        
    if len(codes) > 0:
        print('  Codes apparently found!')
        logging.debug(headline)
        logging.debug(f'URL: {url}')
        
        try:
            session, csrf_token = mtgaapi.login()
            logging.info('    Successfully logged into MTGA')
        except Exception as e:
            logging.info('    MTGA login failed', e)
            return
        
        retries = []
        for code in codes:
            logging.info(f'    Claiming {code}')
            response = mtgaapi.claimCode(session, csrf_token, code)
            logging.info(f'      {response}')
            if response == 'Not Found':
                retries += codepostprocessor.retryCodes(code)
        
        if len(retries) > 0: logging.info(f'    Trying similar codes...')
        for retryCode in retries:
            logging.info(f'      Claiming {retryCode}')
            response = mtgaapi.claimCode(session, csrf_token, retryCode)
            logging.info(f'        {response}')
            
    else:
        print('  No codes found')
    return codes


def parallelOCRProcessing(imgs, n):
    q = multiprocessing.Queue()
    allProcesses = []
    for i in range(n):  
        p = multiprocessing.Process(target=imageocr.parseImages, args=(imgs[i*len(imgs)//n:(i+1)*len(imgs)//n], q, ), daemon=True)
        allProcesses.append(p)
        p.start()
    for p in allProcesses:
        p.join()
    codes = []
    while q.qsize():
        codes += [q.get()]
    return codes

def initLogs():
    # DEBUG to file, INFO to file and console
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m %H:%M', filename=LOG_FILE, filemode='a')
    # Second stream to still print in console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(console)
    
    # other module logs pollute mines
    logging.getLogger('PIL').setLevel(logging.WARNING)
    for log_name, log_obj in logging.Logger.manager.loggerDict.items():
        log_obj.disabled = True

def shorten(text, maxChars=40):
    return text if len(text) <= maxChars else text[:maxChars] + '...'

