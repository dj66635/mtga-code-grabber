import multiprocessing
import redditapi
import discordapi
import processor

def main():
    with open('art.txt') as f: header = f.read()
    print(header)
    
    postsQueue = multiprocessing.Queue()
    r = multiprocessing.Process(target=redditapi.listenToReddit, args=(postsQueue, ), daemon=True)
    d = multiprocessing.Process(target=discordapi.listenToDiscord, args=(postsQueue, ), daemon=True)
    r.start()
    d.start()
    
    try:
        while True:
            source, title, content, contentType = postsQueue.get()
            processor.process(source, title, content, contentType)
            
    except KeyboardInterrupt:
        print('Ending...')

if __name__ == '__main__':
    main()
   