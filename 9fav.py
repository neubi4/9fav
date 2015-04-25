from optparse import OptionParser
import requests
from bs4 import BeautifulSoup

def loadItems(user, loadMoreUrl = ""):
    cookies = dict(safemode='0')
    if not loadMoreUrl:
        r = requests.get("http://9gag.com/u/%s/likes" % user, headers={'accept': 'application/json'}, cookies=cookies)
    else:
        r = requests.get("http://9gag.com" + loadMoreUrl, headers={'accept': 'application/json'}, cookies=cookies)
    return r.json()['items'], r.json()['loadMoreUrl']

def parseHtml(html):
    soup = BeautifulSoup(html)
    gif = soup.select("div.badge-animated-container-animated")

    if len(gif):
        return "gif"
    else:
        return "jpg"

def downloadImage(url, image_id, typ, target):
    size = "700b"
    if typ == "gif":
        size = "460sa"

    final_url = url % (image_id, size, typ)
    final_file = "./downloads/%s_%s.%s" % (image_id, size, typ)

    print "downloading %s writing to %s" % (final_url, final_file)
    r = requests.get(final_url)
    with open(final_file, 'a') as imgfile:
        imgfile.write(r.content)
        imgfile.close()

parser = OptionParser()
(options, args) = parser.parse_args()

user = args[0]
gag_image_url = "http://img-9gag-ftw.9cache.com/photo/%s_%s.%s"
loadMoreUrl = ""
counter = 0

while True:
    items, loadMoreUrl = loadItems(user, loadMoreUrl=loadMoreUrl)
    item_count = len(items)
    counter += item_count

    print "found %s items, parsing" % len(items)

    for (key, item) in items.items():
        typ = parseHtml(item)
        downloadImage(gag_image_url, key, typ, "./downloads")

    print "downloaded %s images" % counter

    if item_count < 10:
        break
