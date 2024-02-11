import PIL
import io
import imagepreprocessor
import imageocr
import coderegex
import codepostprocessor
import mtgaapi
from constants import IMG, TXT

def process(source, title, content, contentType):
    print("-" * 80)
    print(f'New {source} Post - Title: {shorten(title)} - Content Type: {contentType}')
    
    if contentType == IMG:
        img = PIL.Image.open(io.BytesIO(content))
        print('  Preprocessing image...')
        imgs = imagepreprocessor.preProcess(img)
        print('  OCR-processing image...')
        codes = set(flatten([imageocr.parseImage(img) for img in imgs]))
        print('  Looking for codes...')
        codes = [codepostprocessor.postProcess(code) for code in codes]
                    
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

        for code in codes:
            print(f'    Claiming {code}')
            response = mtgaapi.claimCode(session, csrf_token, code)
            print(f'    {response}')
            if response == 'Not Found':
                # Retry strategy
                retries = codepostprocessor.retryCodes(code)
                for retryCode in retries:
                    print(f'      Retrying... {retryCode}')
                    mtgaapi.claimCode(session, csrf_token, retryCode)
    else:
        print('  No codes found')
    return


def flatten(xss):
    return [x for xs in xss for x in xs]

def shorten(text, maxChars=50):
    return text if len(text) <= maxChars else text[:maxChars] + '...'