import PIL
import io
import multiprocessing
import imagepreprocessor
import imageocr
import coderegex
import codepostprocessor
import mtgaapi
from constants import IMG, TXT

ocr_workers = 2 # number of ocr threads, more than 2/3 doesnt seem to be worth it

def process(source, title, content, contentType):
    print("-" * 100)
    print(f'New {source} Post - Title: {shorten(title)} - Content Type: {contentType}')
    
    if contentType == IMG:
        img = PIL.Image.open(io.BytesIO(content))
        print('  Preprocessing image...')
        imgs = imagepreprocessor.preProcess(img)
        print('  OCR-processing image...')
        codes = set(parallelOCRProcessing(imgs, ocr_workers))
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
        try:
            session, csrf_token = mtgaapi.login()
            print('    Successfully logged into MTGA')
        except Exception as e:
            print('    MTGA login failed', e)
            return
        
        retries = []
        for code in codes:
            print(f'    Claiming {code}')
            response = mtgaapi.claimCode(session, csrf_token, code)
            print(f'      {response}')
            if response == 'Not Found':
                retries += codepostprocessor.retryCodes(code)
        
        print(f'    Trying similar codes...')
        for retryCode in retries:
            print(f'      Claiming {retryCode}')
            response = mtgaapi.claimCode(session, csrf_token, retryCode)
            print(f'        {response}')
            
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


def flatten(xss):
    return [x for xs in xss for x in xs]

def shorten(text, maxChars=50):
    return text if len(text) <= maxChars else text[:maxChars] + '...'

