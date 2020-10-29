import cv2
import numpy as np
import argparse
import json
import os
import urllib
import re

import bs4
from bs4 import BeautifulSoup
import requests
#import concurrent
import threading
import sys


class Google(object):
    def __init__(self):
        self.GOOGLE_SEARCH_URL = "https://www.google.com/search"
        self.session = requests.session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) \
                    Gecko/20100101 Firefox/10.0"
            }
        )

    def search(self, keyword, maximum):
        print("Begining searching %s" % (keyword))
        query = self.query_gen(keyword)
        print("query", query)
        return self.image_search(query, maximum)

    def search_with_url(self, url, maximum):
        print("Begining URL searching %s" % (url))
        query = self.query_gen_url(url)
        print("query", query)
        return self.image_search(query, maximum)

    def query_gen(self, keyword):
        # search query generator
        page = 0
        while True:
            params = urllib.parse.urlencode(
                {"q": keyword, "tbm": "isch", "ijn": str(page)}
            )

            yield self.GOOGLE_SEARCH_URL + "?" + params
            page += 1
            
    def query_gen_url(self,  url):
        # search query generator
        page = 0
        while True:
            yield url + ("&ijn=%d" % page)
            page += 1           

    def image_search(self, query_gen, maximum):
        results = []
        total = 0
        while True:
            # search
            url = next(query_gen)
            print("url= ", url)
            html = self.session.get(url).text
            print("image_search:  %s..." % (html[:200]))
            '''                
            #soup = bs4.BeautifulSoup(html, "lxml")
            soup = bs4.BeautifulSoup(html, "html.parser")
            elements = soup.select(".rg_meta.notranslate")
            jsons = [json.loads(e.get_text()) for e in elements]
            print("elements=", len(elements), "jsons=", len(jsons))
            image_url_list = [js["ou"] for js in jsons]
            print("image_search len", len(image_url_list))
            '''
            image_url_list = re.findall(r'https://[^"]*jpg', html)
            # add search results
            if len(image_url_list) == 0:
                print("-> No more images")
                break
            elif len(image_url_list) > maximum - total:
                results += image_url_list[: maximum - total]
                break
            else:
                results += image_url_list
                total += len(image_url_list)

        print("-> Found", str(len(results)), "images")
        return results

def download_image(url, save_path):
    try:
        raw_img = urllib.request.urlopen(url).read()
        f = open(save_path, 'wb')
        f.write(raw_img)
        f.close()
        print("successful:", save_path, url)
        return True
    except BaseException:
        print("failed:", save_path, url)
        return False

def image_scrap(query=None, url = None, max_images=100, data_dir='/tmp', use_thread=True):
    if not(query is None):
        folder = query.split()
        folder = '_'.join(folder)
        # 複数のキーワードを"+"で繋げる
        query = query.split()
        query = '+'.join(query)
        print("query", query)
    
    os.makedirs(data_dir, exist_ok=True)                
    google = Google()

    # search images
    if url is not None:
        results = google.search_with_url(url, maximum=max_images)
    else:
        results = google.search(query, maximum=max_images)
    # download

    jobs = []
    for i, url in enumerate(results):
        print("url", url)
        save_path = os.path.join(data_dir, "%05d.jpg" % (i+1))
        print("-> Downloading image", save_path, end=" ")
        if use_thread:
            thread = threading.Thread(target=download_image, args=(url, save_path))
            thread.start()
            jobs.append(thread)
        else:
            download_image(url, save_path)

    if use_thread:  #一定時間ダウンロードできないものは打ち切り
        [job.join(60) for job in jobs]

def main():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument("-t", "--query", help="query keywords", type=str, required=False)
    parser.add_argument("-u", "--url", help="url list text file", type=str, default=None, required=False)
    parser.add_argument(
        "-n", "--number", help="number of images", type=int, required=False, default=10000
    )
    parser.add_argument(
        "-d", "--directory", help="download location", type=str, default="data"
    )
    args = parser.parse_args()
    print("imagescraping")
#    print(args)

    if args.url is not None:
        print("url", args.url)
        with open(args.url) as f:
            for i, url in enumerate(f):
                image_scrap(url=url, max_images=args.number, data_dir=args.directory)
    else:
        image_scrap(query=args.query, max_images=args.number, data_dir=args.directory)

if __name__ == '__main__':
    main()
    print("all done")
    sys.exit()
    


    
    

    
