#!/usr/bin/env python

# Copyright (C) 2011 - 2012 Sebastian Ruml <sebastian.ruml@gmail.com>
#
# This file is part of YATIR.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 1, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__appName__ = 'yatir'
__author__ = 'sebastian.ruml@gmail.com'
__version__ = '0.2'

import sys
import os
import getopt
import argparse
import ConfigParser
import urllib
import time
from datetime import date, datetime, time
from tumblr import Api

# Configuration directory name
conf_dir = os.path.join(os.path.expanduser('~'), '.' + __appName__)

# Default config
DEFAULT_CONFIG = """[general]
blogs_file: blogs.txt
download_dir: images
max_images_to_download: 50
"""

class Configuration():
  blogs_file_name = ""
  max_number_of_images = 0
  download_dir = ""

  def __init__(self):
    # Check if the config directory exists
    global conf_dir
    if not os.path.exists(conf_dir):
      try:
        os.makedirs(conf_dir)
      except OSError, error:
        raise Exception(error)

    # Check if the config file exists
    self.config_file_name = os.path.join(conf_dir, "config.ini")
    if not os.path.exists(self.config_file_name):
      try:
        f = open(self.config_file_name, 'w')
      except IOError, error:
        raise Exception("Could not create %r : %s" % (self.config_file_name, error))

      f.write(DEFAULT_CONFIG)
      f.close()

    # Read the config file
    self.read_config()

  def read_config(self):
    config = ConfigParser.ConfigParser()
    config.read(self.config_file_name)

    self.blogs_file_name = config.get('general', 'blogs_file')
    self.max_number_of_images = config.get('general', 'max_images_to_download')
    self.download_dir = config.get('general', 'download_dir')
    if not os.path.isabs(self.download_dir):
      self.download_dir = os.path.join(os.getcwd(), self.download_dir)
      print self.download_dir


# Global configuration object
config = None


def download_image(url, target):
  """
  This function downloads an image from the given URL and saves
  it to the given target.
  """
  try:
    webFile = urllib.urlopen(url)
    targetFile = open(target, 'w')
    targetFile.write(webFile.read())
    webFile.close()
    targetFile.close()
  except:
    print "Error downloading image"


def read_blogs(blogs, download_dir):
  global config

  # Check if the download dir exists; if not create it
  if not os.path.exists(download_dir):
    os.mkdir(download_dir)

  # Process all given blogs
  for blog in blogs:
    # Check if the target dir exists; if not create it
    target_dir = os.path.join(download_dir, blog)
    if not os.path.exists(target_dir):
      os.mkdir(target_dir)

    print "Downloading images from " + blog + " to " + target_dir + "..."

    try:
      site_url = blog
      api = Api(site_url)
      posts = api.read(start=0, max=config.max_number_of_images)
      #posts = api.read(start=0)
    except:
      print "error"

    imageCounter = 1
    for post in posts:
      try:
        url = post['photo-url-1280']
        photo_caption = post['photo-caption']
        slug = post['slug']
        post_date_str = post['date-gmt']
      except:
        print "error"

      image_name = url.rsplit('/', 1)[1]
      # Check if a file extension is given
      supported_file_types = ['jpg', 'jpeg', 'png', 'gif']
      if not image_name[-3:] in supported_file_types:
        # Add an extension to the image name
        image_name = image_name + ".jpg"
      image_file_name = blog + "_-_" + image_name
      target_file_name = os.path.join(target_dir, image_file_name)

      # Check if file already exists
      if os.path.exists(target_file_name):
        print "Image already exists."
        imageCounter += 1
        continue

      if imageCounter > config.max_number_of_images:
        break

      print "Downloading image Nr " + str(imageCounter) + ": \"" + image_file_name + "\" ..."
      download_image(url, target_file_name)
      imageCounter += 1


def parse_blogs_file(filename):
  """
  Reads all entries in the given blogs file
  """
  if filename == None:
    return

  file = None
  global config

  # Check if the file exists
  try:
    file = open(filename, 'r')
  except IOError as e:
    print "Could not read sites file. Please, check if the blogs file exists."
    print "Name of the file: " + filename
    sys.exit(2)

  lines = file.readlines()

  blogs = []
  for line in lines:
    line = line.rstrip()

    # Check for comments
    if line.startswith('#'):
      continue

    blogs.append(line)

  return blogs


def print_sites():
  pass


def usage():
    print "tumblr_downloader.py {options} {sites file|Tumblr blog URL}\n"
    print "Options are..."
    print "\t-t, --download-dir\tSpecifies the directory where the images will be downloaded to."
    print "\t--site-file\t\tFile that contains a sequence of Tumblr blog ULRs. Every line contains one URL."
    print "\t--site\t\t\tDownload images from the given Tumblr blog URL."
    print "\t--today\t\t\tDownload only images for today."
    print "\t--start-item\t\t\tTODO"
    print "\t--max-items\t\t\tTODO"
    print "\t--start-date\t\t\tTODO"
    print "\t--duration\t\t\tTODO"
    print "\t--print-sites\t\tPrints all Tumblr blog URLs from the default blog file to the standard output."
    print "\t-h, --help\t\tDisplay this help message."


def main():
  global config

  parser = argparse.ArgumentParser()
  parser.add_argument("blog", nargs='?', help="Tumblr blog name to download images from (only the blog name, without .tumblr.com)")
  parser.add_argument("--max-images", type=int, help="The maxmium number of images that should be downloaded from one blog")
  parser.add_argument("--blog-file", help="Read blogs from this file instead from the file specified in the config file")
  parser.add_argument("-d", "--download-dir", help="Target directory for the downloaded images")
  parser.add_argument("-V", help="Shows the version and exits", action="store_true")
  args = parser.parse_args()

  # Print version number and exit
  if args.V:
    print __appName__ + " v" + __version__
    sys.exit(1)

  # Read config file
  global config
  config = Configuration()

  if args.blog_file:
    config.blogs_file_name = args.blog_file

  if args.download_dir:
    config.download_dir = args.download_dir

  if args.max_images:
    config.max_number_of_images = args.max_images

  if args.blog:
    read_blogs([args.blog], config.download_dir)
  else:
    # Check if the blogs file exists
    try:
      blogs_file = open(config.blogs_file_name, 'r')
    except IOError as e:
      print "Could not read the blogs file. Please, check if the file exists."
      print "Name of the file: " + config.blogs_file_name
      sys.exit(1)

    # Read all blogs from the file
    blogs = parse_blogs_file(config.blogs_file_name)

    # No blogs given
    if len(blogs) < 1:
      print "No Tumblr blogs specified!"
      sys.exit(1)

    # Read all blogs and download images
    read_blogs(blogs, config.download_dir)


if __name__ == "__main__":
  try:
    main()
  except (KeyboardInterrupt, SystemExit):
    sys.exit(1)
  except:
    import traceback
    traceback.print_exc()

