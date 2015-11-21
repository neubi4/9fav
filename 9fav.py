import requests, argparse, os, sys
from bs4 import BeautifulSoup
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Downloads all 9gag images from a user')
parser.add_argument('username', help='9gag username')
parser.add_argument('--dir', '-d', help='download directory', default="downloads")
parser.add_argument('--count', '-c', help="worker_count", type=int, default=4)
args = parser.parse_args()

gag_image_url = "http://img-9gag-ftw.9cache.com/photo/%s_%s.%s"
default_headers = {
    'accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}
download_path = os.path.realpath(args.dir)

def loadItems(user, loadMoreUrl = ""):
    cookies = dict(safemode='0')
    if not loadMoreUrl:
        r = requests.get("http://9gag.com/u/%s/likes" % user, headers=default_headers, cookies=cookies)
    else:
        r = requests.get("http://9gag.com" + loadMoreUrl, headers=default_headers, cookies=cookies)
    return r.json()['items'], r.json()['loadMoreUrl']

def parseHtml(html):
    soup = BeautifulSoup(html, "html.parser")
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
    final_file = "%s/%s_%s.%s" % (target, image_id, size, typ)

    if os.path.isfile(final_file):
        print "%s already downloaded" % (final_file)
        return

    print "downloading %s writing to %s" % (final_url, final_file)
    r = requests.get(final_url)
    with open(final_file, 'a') as imgfile:
        imgfile.write(r.content)
        imgfile.close()

def check_download_dir():
    if (not os.path.exists(download_path)) or (not os.access(download_path, os.W_OK)):
        print "%s does not exists or is not writeable" % (download_path)
        sys.exit(1)

if __name__ == "__main__":
    check_download_dir()
    loadMoreUrl = ""
    counter = 0
    worker_pool = Pool(processes=args.count)
    try:
        while True:
            items, loadMoreUrl = loadItems(args.username, loadMoreUrl=loadMoreUrl)
            item_count = len(items)
            counter += item_count

            print "found %s items, parsing" % len(items)

            for (key, item) in items.items():
                typ = parseHtml(item)
                worker_pool.apply_async(downloadImage, [gag_image_url, key, typ, download_path])

            print "downloaded %s images" % counter

            if item_count < 10:
                break

        worker_pool.close()
        worker_pool.join()
        print "all imaged downloaded"
    except KeyboardInterrupt:
        worker_pool.terminate()
