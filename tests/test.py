import sys
sys.path.append(r'..\codegrabber')
sys.path.append(r'..\mtga-code-grabber\codegrabber')
import os
os.chdir('..')

import PIL
import io
import time
from codegrabber import redditapi
from codegrabber import processor
from codegrabber import imagepreprocessor
from codegrabber import imageocr
from codegrabber import coderegex
from codegrabber import codepostprocessor
from codegrabber import mtgaapi
from codegrabber.constants import IMG, TXT

''' Tests / Samples '''
samples = [
        ('https://new.reddit.com/r/MagicArena/comments/1ai1blb/free_code/', 
         ['EFD8D-7DBE2-BEB02-36638-F8D00']),
        ('https://new.reddit.com/r/MagicArena/comments/1aifurw/pre_release_codes_for_you_mf/', 
         ['CB091-BC6D4-C50E6-C4543-A6835']),
        ('https://new.reddit.com/r/mtg/comments/1anm3eo/enjoy/',
         ['54B72-BAC76-2200C-01C9F-DC594']),
        ('https://new.reddit.com/r/mtg/comments/1ahlqv6/prerelease_code/', 
         ['3DE79-73AA6-54149-BBA23-65464']),
        ('https://new.reddit.com/r/MagicArena/comments/1agx4zk/free_code/', 
         ['2B946-CD9FB-C0AD3-CF4C8-AAB70']),
         
        ('https://new.reddit.com/r/mtg/comments/1aiaw43/arena_codes/', 
         ['08A49-510F7-58392-A28A1-AE539', '089C8-A5EB8-DD9F4-C3BFA-FA46A']),
        ('https://new.reddit.com/r/mtg/comments/1aiejrx/free_codes/', 
         ['1930B-A8592-97D93-EC138-9EF98', '16C22-D24A5-10D7F-54243-9638E']),
        ('https://new.reddit.com/r/MagicArena/comments/1akgt7p/up_for_grabs/',
         ['92DDF-5890E-4C15C-CDF14-53EA0', '281B2-F10D3-41134-860F2-06C2E']),
        ('https://new.reddit.com/r/MagicArena/comments/1an1faf/codes_will_be_posting_more_over_the_next_few/', 
         ['DFF0A-4B4D8-42AA0-92918-6A94C', 'D976E-82186-B44CE-17AB0-6DEB0']),

        ('https://new.reddit.com/r/MagicArena/comments/1anwoux/c0des/',
         ['15000-BD429-DCB37-3C411-CA075', 'DEFDF-D45E6-7E605-59A29-77C1A', '1500D-1FFEA-92B12-B79B5-97231']),
        ('https://new.reddit.com/r/MagicArena/comments/1aptx8q/prerelease_codes/',
         ['4E662-86331-95B6E-055E0-33375', '4E8A2-9317D-3E83E-ED4C5-C99BC', '4EC24-EAE99-73366-9BF7A-B6B2A']),
         
        ('https://new.reddit.com/r/mtg/comments/1ajpjlf/some_mtg_arena_codes_enjoy/', 
         ['5642F-EBB64-DDFC3-A3DC1-9D647','1F08F-4C0ED-08CA9-6E234-E1EC8','563F7-A51EE-61DB6-443C8-C4FC8','563F8-49D11-4412E-8CA36-A97F5']),
        ('https://new.reddit.com/r/mtg/comments/1ajs5cz/mtg_arena_codes/',
         ['1EDC2-DBD5D-69C50-6AA42-83BF0','08068-3594F-36FE7-1DDDF-68A4B','676C2-0E712-946E5-0B5DC-956CC','23002-3A930-4B2B8-C42C2-36016']),
        ('https://new.reddit.com/r/MagicArena/comments/1anln6b/more_codes/',
         ['41093-6FC4F-08A06-BFA9D-B99A7','3A1CB-CD6B3-87D9C-0ADB9-D6690','40D23-444C7-77606-7E7B0-87115','D73E3-2AC0C-8C837-DA6F0-1A1E1']),
        
        ('https://new.reddit.com/r/MagicArena/comments/1ajsqk0/feedind_the_bots/', 
         ['A9FD8-675E0-2528F-1FBC3-229B0','FE69E-54E2C-91646-A8B37-6A167','A91ED-652AF-AD804-23EF7-1B2E9','D9305-EA464-FD6FA-9716E-DBC46','4CF66-7923B-D0F7D-4A6FE-FD855','2A3CC-DBB83-D3F85-F5968-7123F']),
        ('https://new.reddit.com/r/MagicArena/comments/1amjlmn/new_codes/', 
         ['66922-03777-F05F5-484FD-1FE12','7DEAE-057E8-B7869-DE087-D341A','533FF-2B352-6FFC8-3C2E1-297E9','77474-C8E27-ED24A-24420-5979B','7DE9A-6612C-74428-72DEF-4D85A','7DE85-09764-673EF-8905B-7F075'])   
        ]
              
sampleTxt = [('https://new.reddit.com/r/MagicArena/comments/1akxex1/streets_of_new_capenna_prerelease_arena_codes/',['C2296-9F534-0C8CD-ABFD6-70EC7', 'B86FE-715E9-F3A1D-869DD-388D4', 'C22DF-5A380-E3355-F1DAC-BB64F', 'C4BE5-95C57-95356-79629-0227F', 'C3FB1-3AC79-8C81F-49393-DE536'])]
sampleHard = [('https://new.reddit.com/r/MagicArena/comments/1aiqhnj/people_still_like_codes_hint_assassins_creed/', [])]
samplePath1 = r'tests\20240207_203859.jpg'
samplePath2 = r'tests\IMG_5056.jpg'

def timeIt(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Elapsed time: {round(end - start, 2)}s')
        return result
    return wrapper

@timeIt
def batchRedditTest(samples, optimisticMode=False, n=1, debug=0):
    totalCodes = 0
    totalFound = [0,0,0]
    for sample in samples:
        sampleUrl, codeAnswers = sample
        totalCodes += len(codeAnswers)
        found = singleRedditTest(sample, optimisticMode, n, debug)
        totalFound = [totalFound[i] + found[i] for i in range(3)]
        print('-' * 40)
    ratio = round((totalFound[2] / totalCodes) * 100, 1)
    print(f'> Found {totalFound[0]} codes out of {totalCodes} (OCR)')
    print(f'> Found {totalFound[1]} codes out of {totalCodes} (PostProcess)')
    print(f'> Found {totalFound[2]} codes out of {totalCodes} (Retrial)')
    print(f'> Ratio: {ratio}%')
    
@timeIt
def singleRedditTest(sample, optimisticMode=False, n=1, debug=0):
    sampleUrl, codeAnswers = sample
    print(f'Url: {sampleUrl}')
    submission = redditapi.reddit.submission(url=sampleUrl) 
    responses = redditapi.readSubmission(submission)
    
    totalCodes = [[], [], []]
    for response in responses:
        _, _, _, content, contentType = response
        ocrCodes, postCodes, codes = processTest(content, contentType, optimisticMode, n, debug)
        if debug >= 2:
            print(f'ImageOCR codes: {ocrCodes}')
            print(f'Postprocessed codes: {codes}')
        totalCodes[0] += ocrCodes
        totalCodes[1] += postCodes
        totalCodes[2] += codes

    found = [sum(e in set(codeAnswers) for e in set(totalCodes[i])) for i in range(3)]
    print(f'> Found {found[0]} out of {len(codeAnswers)} (OCR)')
    print(f'> Found {found[1]} out of {len(codeAnswers)} (PostProcess)')
    print(f'> Found {found[2]} out of {len(codeAnswers)} (Retrial)')
    return found

def processTest(content, contentType, optimisticMode=False, n=1, debug=0):
    if contentType == IMG:
        img = PIL.Image.open(io.BytesIO(content))
        if debug >= 1: display(img.resize(int(0.2*s) for s in img.size))
        imgs = imagepreprocessor.preProcess(img, optimisticMode, debug)
        if debug >= 1: print(f'Number of imgs after preprocessing: {len(imgs)}')
        ocrCodes = processor.parallelOCRProcessing(imgs, n)  
        #ocrCodes = set(flatten([imageocr.parseImage(img) for img in imgs]))          
    elif contentType == TXT:
        ocrCodes = coderegex.findCode(content)
    else:
        print('  Unsupported content type')  
    postCodes = [codepostprocessor.postProcess(code) for code in ocrCodes]
    codes = postCodes + flatten([codepostprocessor.retryCodes(code) for code in postCodes])
    return ocrCodes, postCodes, codes

@timeIt
def claimTest(codes):
    session, csrf_token = mtgaapi.login()
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
    
def singleFileTest(path, optimisticMode=False, n=1, debug=0):
    print(f'Path {path}')
    img = PIL.Image.open(path)
    imgs = imagepreprocessor.preProcess(img, optimisticMode, debug)
    codes = processor.parallelOCRProcessing(imgs, n)  
    if debug >= 2: print(f'ImageOCR codes: {codes}')  
    codes = [codepostprocessor.postProcess(code) for code in codes]
    
def flatten(xss):
    return [x for xs in xss for x in xs]
    
'''
Some quick tests
    
Config | Accuracy | Time | Comments
------------------------------------

Default | 38/40 | 332s | almost idle background
Default | 37/40 | 513s | high background load (affects its accuracy too, maybe because of timeout)

Default 0.3 contour_th | 38/40 | 344s | very similar
Default 160,200 th     | 38/40 | 350s | very similar

Only cropMinAreaRect   | 32/40 | 226s | slightly worse accuracy, faster -> maybe "optimistic mode"
Only cropBoundingRect  | 28/40 | 238s | worse accuracy, faster
No erode               | 28/40 | 244s | worse accuracy, faster

Erode then resize | 34/40 | 345s | worse
Size 550-103      | 35/40 | 460s | worse
Size 750-143      | 32/40 | 589s | worse
No resize         | 32/40 | 592s | worse

------------------------------------

Default | 38/40 | 210s | 2 threads
Default | 38/40 | 160s | 3 threads

'''
