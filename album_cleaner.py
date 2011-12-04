import urllib, os
from datetime import *
from xml.dom import minidom
import markup

PICASA_URL = 'https://picasaweb.google.com/data/feed/base/user/shiauru1210/albumid/5573533753388088017?alt=rss&kind=photo&hl=en_US'
OUT_DIR = "target"

import Image
from ExifTags import TAGS

def get_exif(fn):
  """Routine recuperee sur le net"""
  ret = {}
  i = Image.open(fn)
  info = i._getexif()
  for tag, value in info.items():
    decoded = TAGS.get(tag, tag)
    ret[decoded] = value
  return ret

def download_images_from_picasa(url, folder):
  """Telecharge et parse un album picasa
  
  Ce code n'a ete teste que sur l'album utilise en exemple
  """
  dom = minidom.parse(urllib.urlopen(url))
  images = dom.getElementsByTagName('item')
  for im in images:
    title = im.getElementsByTagName('title')[0].childNodes[0].data
    url = im.getElementsByTagName('media:content')[0].getAttribute('url')
    print "Downloading %s at %s" % (title, url)
    urllib.urlretrieve(url, "%s/%s" % (folder, title))

def images_in(dir):
  """Liste toutes les images d'un repertoire en leur
  ajoutant des exifs
  """
  images = []
  for im in os.listdir(dir):
    if im[-3:] not in ['jpg','JPG']:
      continue
    exifs = get_exif("%s/%s" % (dir, im))
    date = datetime.strptime(exifs['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
    images.append({'date': date, 'image':'%s/%s' % (dir, im), 'exifs':exifs})
  return images
  

def group_by_date(images, threshold = timedelta(minutes = 5)):
  """Regroupe les photos prises a un interval inferieur
  a threshold
  
  Avec le delta default, l'idee est de regrouper toutes
  les photos prises lors d'une meme sortie d'appareil
  """
  images.sort(key = lambda x: x['date'])
  
  groups = [[images.pop(0)]]
  while len(images)>0 :
    image = images.pop(0)
    if image['date'] - groups[-1][-1]['date'] < threshold:
      groups[-1].append(image)
    else:
      groups.append([image])
  return groups

def dump_groups(groups, filename="groups"):
  """Imprime une liste de groupes dans un html"""
  page = markup.page()
  page.init()
  for group in groups:
    page.p()
    for im in group:
      page.img(width=120, src='../%s' % im['image'])
    page.p.close()
    page.hr()
  f = open('%s/%s.html' % (OUT_DIR, filename), 'w')
  f.write(page.__str__())
  f.close()
  print "Vous pouvez consulter les groupes ici: %s" % f.name
  
def dump_images(images, filename="images"):
  """Imprime une liste d'images dans un html"""
  page = markup.page()
  page.init()
  for im in images:
    page.img(width=120, src='../%s' % im['image'])
  f = open('%s/%s.html' % (OUT_DIR, filename), 'w')
  f.write(page.__str__())
  f.close()
  print "Vous pouvez consulter ces images ici: %s" % f.name
  
def best_image_in_group(group):
  """Retourne la meilleure image dans un jeu d'image
  
  Ici il s'agit de groupes d'image prise dans un interval
  de temps court. L'heuristique utilisee est donc:
  
  La derniere photo prise est la bonne
  """
  return group[-1]

def main():
  if not os.path.exists(OUT_DIR):
      os.makedirs(OUT_DIR)
      
  if not os.path.exists('images/paris'):
    os.makedirs('images/paris')
    download_images_from_picasa(PICASA_URL, 'images/paris')

  for image_set in ['london', 'paris']:
    images = images_in('images/%s' % image_set)
    groups = group_by_date(images)
    dump_groups(groups, filename="%s_groupes" % image_set)
    images = map(best_image_in_group, groups)
    dump_images(images, filename="%s_final" % image_set)

if __name__ == '__main__':
  main()
