import praw
import requests
from constants import REDDIT, IMG, TXT, PNG, JPG, JPEG
import configparser
import logging

config = configparser.ConfigParser()
config.read('config.ini')

reddit = praw.Reddit(client_id = config['Reddit']['client_id'], 
                     client_secret = config['Reddit']['client_secret'], 
                     user_agent = 'totally_regular_chrome')

pause_after_ = int(config['Reddit']['delay'])

subreddit_names = config['Reddit']['subreddit_names']


def listenToReddit(postsQueue):
    print('Listening to Reddit...')
    subreddit = reddit.subreddit('+'.join(subreddit_names.split(',')))
    # 600 requests in 10 mins is reddit limit
    for submission in subreddit.stream.submissions(skip_existing=True, pause_after=pause_after_):
        if reddit.auth.limits['remaining'] < 20: logging.debug(f'Reaching Reddit rate limit: {reddit.auth.limits["remaining"]}')
        if submission is None: continue
        try:
            responses = readSubmission(submission)
        except Exception as e:
            logging.debug(str(e))
            continue
            
        for response in responses:
            descriptiveName, title, url, content, contentType = response
            postsQueue.put((descriptiveName, title, url, content, contentType))

        
def readSubmission(submission):
    descriptiveName = REDDIT + ' (r/' + submission.subreddit.display_name + ')'
    if hasattr(submission, 'is_gallery'):
        responses = []
        total = len(submission.media_metadata.items())
        n = 1
        for i in submission.media_metadata.items():
            image_url = i[1]['p'][0]['u']
            image_url = image_url.split('?')[0].replace('preview', 'i')
            response = requests.get(image_url)
            responses += [(descriptiveName, f'({n}/{total}) ' + submission.title, reddit.config.reddit_url + submission.permalink, response.content, IMG)]
            n += 1
        return responses
            
    elif submission.url.endswith((PNG, JPG, JPEG)): 
        image_url = submission.url
        response = requests.get(image_url)
        return [(descriptiveName, submission.title, reddit.config.reddit_url + submission.permalink, response.content, IMG)]
    
    else:
        return [(descriptiveName, submission.title, reddit.config.reddit_url + submission.permalink, submission.selftext, TXT)]
