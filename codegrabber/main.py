import multiprocessing
import redditapi
import discordapi
import processor
from constants import ART_FILE

'''

TODO

- fix requirements.txt
- investigate WARNING:prawcore:Retrying due to ReadTimeout(ReadTimeoutError("HTTPSConnectionPool(host='oauth.reddit.com', port=443): Read timed out. (read timeout=16.0)")) status: GET https://oauth.reddit.com/r/magicarena+mtg/new

'''

def main():
    with open(ART_FILE) as f: header = f.read()
    print(header)
    
    processor.initLogs()
    
    postsQueue = multiprocessing.Queue()
    r = multiprocessing.Process(target=redditapi.listenToReddit, args=(postsQueue, ), daemon=True)
    d = multiprocessing.Process(target=discordapi.listenToDiscord, args=(postsQueue, ), daemon=True)
    r.start()
    d.start()
    
    try:
        while True:
            source, title, url, content, contentType = postsQueue.get()
            processor.process(source, title, url, content, contentType)
            
    except KeyboardInterrupt:
        print('Ending...')

if __name__ == '__main__':
    main()
   