import Image,os

from scipy.ndimage import *
from scipy.misc import toimage
from numpy import *

import subprocess

out_dir = "target"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)
    
def detect_blur(f):
  print "Processing %s" % f
  im = Image.open("images/orig_"+f+".jpeg") 
  im = im.convert('F')
  im = array(im)

  im = filters.laplace(im)
  laplacien_im = im
  toimage(im).save(out_dir+"/laplacien_"+f+".png", "png")
  im = morphology.white_tophat(im, (3,3))
  tophat_im = im
  toimage(im).save(out_dir+"/tophat_"+f+".png", "png")
  
  im = filters.percentile_filter(im, 30, 1)

  toimage(im).save(out_dir+"/final_"+f+".png", "png")
  
  subprocess.call("/usr/local/bin/convert %s/final_%s.png %s/ppm_final_%s.ppm" % (out_dir, f, out_dir,f), shell=True)
  
  subprocess.call("./segment/segment 0.8 100 100 %s/ppm_final_%s.ppm %s/segment_%s.ppm" % (out_dir, f, out_dir,f), shell=True)
  
  im_seg = Image.open("%s/segment_%s.ppm" % (out_dir, f))
  im_seg = array(im_seg)
  
  print "laplacien"
  
  laplacian_mask = build_mask(im_seg, laplacien_im)
  toimage(laplacian_mask).save(out_dir+"/laplacian_mask_"+f+".png", "png")
  
  print "tophat"
  
  tophat_mask = build_mask(im_seg, tophat_im, 10)
  toimage(tophat_mask).save(out_dir+"/tophat_mask_"+f+".png", "png")
  
def build_mask(im, criterion, limit=0.5):
  criterions = dict()
  for i in range(len(im)):
    for j in range(len(im[0])):
      key = "%i %i %i" % tuple(im[i, j])
      if key not in criterions:
        criterions[key] = [criterion[i,j], 1, 0]
      else:
        criterions[key][0] += criterion[i,j]
        criterions[key][1] += 1
  
  moy = 0
  vals = []
  
  for seg in criterions:
    criterions[seg][2] = criterions[seg][0] / criterions[seg][1]
    moy += abs(criterions[seg][2])
    vals.append(abs(criterions[seg][2]))
    
  moy /= len(criterions)

  im_mask = zeros_like(criterion)
  for i in range(len(im)):
    for j in range(len(im[0])):
      key = "%i %i %i" % tuple(im[i, j])
      
      if(abs(criterions[key][2])>moy*0.3):
        im_mask[i,j] = 255
      else:
        im_mask[i,j] = 0
      #print im_mask[i,j]

  return im_mask
  

for im in ["carla", "matt", "camargue", "tree", "golf", "conchords"]:
  detect_blur(im)