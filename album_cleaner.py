import urllib, os
from datetime import *
from xml.dom import minidom
import markup, webbrowser

PICASA_URL = 'https://picasaweb.google.com/data/feed/base/user/shiauru1210/albumid/5573533753388088017?alt=rss&kind=photo&hl=en_US'

out_dir = "target"

import Image
from ExifTags import TAGS

def get_exif(fn):
  ret = {}
  i = Image.open(fn)
  info = i._getexif()
  for tag, value in info.items():
    decoded = TAGS.get(tag, tag)
    ret[decoded] = value
  return ret

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def download_images_from_picasa(url):
  dom = minidom.parse(urllib.urlopen(url))
  images = dom.getElementsByTagName('item')
  for im in images:
    title = im.getElementsByTagName('title')[0].childNodes[0].data
    url = im.getElementsByTagName('media:content')[0].getAttribute('url')
    print "Downloading %s at %s" % (title, url)
    urllib.urlretrieve(url, "%s/%s" % (out_dir, title))

DATE_THRESHOLD = timedelta(seconds = 15)

def classify_by_date():
  images = []
  for im in os.listdir(out_dir):
    if im[-3:] not in ['jpg','JPG']:
      continue
    exifs = get_exif("%s/%s" % (out_dir, im))
    date = datetime.strptime(exifs['DateTime'], "%Y:%m:%d %H:%M:%S")
    print "Date of shot is %s" % date
    images.append({'date': date, 'image':im})
  
  images.sort(key = lambda x: -x['date'].microsecond)
  
  groups = [[images.pop()]]
  while len(images)>0 :
    image = images.pop()
    if groups[0][0]['date']-image['date'] < DATE_THRESHOLD:
      groups[0].insert(0,image)
    else:
      groups.insert(0, [image])
  
  return groups

def view_groups(groups):
  page = markup.page()
  page.init(title="Demo du grouping")
  for group in groups:
    page.p()
    for im in group:
      page.img(width=60, src=im['image'])
    page.p.close()
  f = open('target/out.html', 'w')
  f.write(page.__str__())
  f.close()
  print f.name

download_images_from_picasa(PICASA_URL)
groups = classify_by_date()
view_groups(groups)