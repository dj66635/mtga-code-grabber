import sys
sys.path.append(r'..\codegrabber')
sys.path.append(r'..\mtga-code-grabber\codegrabber')
import os
os.chdir('..')

import PIL
import io
import time
import requests
import json
from codegrabber import redditapi
from codegrabber import discordapi
from codegrabber import processor
from codegrabber import imagepreprocessor
from codegrabber import imageocr
from codegrabber import coderegex
from codegrabber import codepostprocessor
from codegrabber import mtgaapi
from codegrabber import constants

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

def batchRedditTest(samples, debug=0):
    start = time.time()
    totalCodes = 0
    totalFound = 0
    for sample in samples:
        sampleUrl, codeAnswers = sample
        totalCodes += len(codeAnswers)
        totalFound += singleRedditTest(sample, debug)
        print('-' * 40)
    ratio = round((totalFound / totalCodes) * 100, 1)
    print(f'> Found {totalFound} codes out of {totalCodes}: {ratio}%')
    end = time.time()
    print(f'Elapsed time: {end - start}s')
    
    
def singleRedditTest(sample, debug=0):
    sampleUrl, codeAnswers = sample
    print(f'Url: {sampleUrl}')
    submission = redditapi.reddit.submission(url=sampleUrl) 
    responses = redditapi.readSubmission(submission)
    totalCodes = []
    found = 0
    for response in responses:
        codes = []
        _, _, content, contentType = response
        if contentType == "img":
            img = PIL.Image.open(io.BytesIO(content))
            codes = singleImageTest(img, debug)
        elif contentType == "txt":
            print(content)
            codes = coderegex.findCode(content)
            if debug >= 2: print(f'Txt codes: {codes}')
        else:
            print("Unsupported type")
        codes = [codepostprocessor.postProcess(code) for code in codes]
        codes += flatten([codepostprocessor.retryCodes(code) for code in codes])
        if debug >= 2: print(f'Postprocessed codes: {codes}')
        totalCodes += codes
    found = sum(e in set(codeAnswers) for e in set(totalCodes))
    print(f'> Found {found} out of {len(codeAnswers)}')
    return found
    
def singleFileTest(path, debug=0):
    print(f'Path {path}')
    img = PIL.Image.open(path)
    singleImageTest(img, debug)
    
def singleImageTest(img, debug):
    if debug >= 1: display(img.resize(int(0.2*s) for s in img.size))
    imgs = imagepreprocessor.preProcess(img, debug)
    codes = set(flatten([imageocr.parseImage(img, debug) for img in imgs]))
    if debug >= 2: print(f'ImageOCR codes: {codes}')
    return codes

def claimTest(codes):
    session, csrf_token = mtgaapi.login()
    for code in codes:
        print(f'Claiming {code}')
        response = mtgaapi.claimCode(session, csrf_token, code)
        print(response)
        if response == 'Not Found':
            retries = codepostprocessor.retryCodes(code)
            for retryCode in retries:
                print(f' Retrying... {retryCode}')
                mtgaapi.claimCode(session, csrf_token, retryCode)

def quickClaimReddit(redditUrl):
    submission = redditapi.reddit.submission(url=redditUrl)
    title, content, contentType = redditapi.readSubmission(submission)
    processor.process('', title, content, contentType)
    
def discordTest(channelID):
    url = constants.DISCORD_URL + constants.CHANNELS_ENDPOINT + channelID
    response = requests.get(url, headers=discordapi.headers)
    j = json.loads(response.content)
    lMId = j['last_message_id']
    print(lMId)
    url = constants.DISCORD_URL + '/guilds/' + j['guild_id']
    response2 = requests.get(url, headers=discordapi.headers)
    h = json.loads(response2.content)
    channelName = j['name']
    guildName = h['name']
    text = f'# {channelName} @ {guildName}'
    print(text)
    
    
def flatten(xss):
    return [x for xs in xss for x in xs]