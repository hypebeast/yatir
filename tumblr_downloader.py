#!/usr/bin/env python

# Copyright (C) 2011 Sebastian Ruml <sebastian.ruml@gmail.com>
#
# This file is part of TumblrDownloader
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

__author__ = 'sebastian.ruml@gmail.com'
__version__ = '0.1'

import sys
import os
import getopt
import urllib
import time
from datetime import date, datetime, time
from tumblr import Api

# Default file name for the site file
SITE_FILE_NAME="sites.csv"

# Default download dir
DOWNLOAD_DIR="downloads"

# This dictionary contains all available tumblr sites
sites = {}

def download_image(url, name):
	try:
		webFile = urllib.urlopen(url)
		localFile = open(name, 'w')
		localFile.write(webFile.read())
		webFile.close()
		localFile.close()
	except:
		print "Error downloading image"


def readTumblr(site_name, site_url, start_item, max_items, download_dir, today=False):
	# Check if the download dir exists; if not create it
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    # Check if the target dir exists; if not create it
    target_dir = os.path.join(download_dir, site_name)
    if not os.path.exists(target_dir):
		os.mkdir(target_dir)

    print "Start downloading from " + site_name + " to " + target_dir

    try:
		api = Api(site_url)
		#posts = api.read(start=start_item, max=max_items)
		posts = api.read(start=start_item)
    except:
		print "error"

    index = 1
    for post in posts:
        try:
            url = post['photo-url-1280']
            photo_caption = post['photo-caption']
            slug = post['slug']
            post_date_str = post['date-gmt']
        except:
			print "error"

        post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S GMT")
        current_time = datetime.today()

        if today:
            if post_date.day() < current_time.day():
                return

        if url == None or slug == None:
            return

        if target_dir == None:
			target_file_name = slug + ".jpg"
        else:
            target_file_name = os.path.join(target_dir, slug + "-" + post_date.strftime("%Y-%m-%d") + ".jpg")

        # Check if file already exists
        if os.path.exists(target_file_name):
            print "Filename exists. Try finding new name..."
            continue

            #exists = True
            #extension_nr = 1
            #while exists:
                # TODO: Check for hash code to identify the already downloaded images
                #if target_dir == None:
                    #image_name = slug + "_" + str(extension_nr) + ".jpg"
                #else:
                    #image_name = os.path.join(target_dir, slug + "_" + str(extension_nr) + ".jpg")

                #if os.path.exists(image_name):
                    #pass
                #else:
                    #exists = False

        print "Downloading image Nr " + str(index) + ": \"" + target_file_name + "\" ..."
        download_image(url, target_file_name)
        index += 1

        if index > max_items:
            return


def read_sites_file(filename):
    if filename == None:
        return

    file = None

    # Check if the file exists
    try:
        file = open(filename, 'r')
    except IOError as e:
        print "Could not read sites file. Please, check if the sites file exists."
        usage()
        sys.exit(2)

    lines = file.readlines()

    for line in lines:
        line = line.rstrip()

        # Check for comments
        if line.startswith('#'):
            continue

        parts = line.split(' ')
        if len(parts) == 2:
            sites[parts[0]] = parts[1]


def print_sites():
	for k,v in sites.iteritems():
		print "Site name: \"" + k + "\" URL: \"" + v + "\""


def usage():
    print "tumblr_downloader.py {options} {sites file|Tumblr blog URL}\n"
    print "Options are..."
    print "\t-t, --download-dir\tSpecifies the directory where the images will be downloaded."
    print "\t--site-file\t\tFile that contains a sequence of Tumblr blog ULRs. Every line contains one URL."
    print "\t--site\t\t\tDownload images from the given Tumblr blog URL."
    print "\t--today\t\t\tDownload only images only from today."
    print "\t--start-item\t\t\tTODO"
    print "\t--max-items\t\t\tTODO"
    print "\t--start-date\t\t\tTODO"
    print "\t--duration\t\t\tTODO"
    print "\t--print-sites\t\tPrints all Tumblr blog URLs from the default blog file to the standard output."
    print "\t-h, --help\t\tDisplay this help message."


def main(argv):
    # Default config
    start = 0
    maxitems = 20
    target = None
    today = False
    site_file = None
    site = None
    target = DOWNLOAD_DIR

    try:
        opts, args = getopt.getopt(argv, "hs:m:t:V", ["site-file=", "help", "start-item=", "max-items=", "download-dir=", "site=", "print-sites", "start-date=", "duration=", "today"])
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit(2)
            elif opt in ("-s", "--start-item"):
                start = int(arg)
            elif opt in ("-m", "--max-items"):
                maxitems = int(arg)
            elif opt in ("-t", "--download-dir"):
                target = arg
            elif opt in ("--site"):
                site = arg
            elif opt in ("--site-file"):
                site_file = arg
            elif opt in ("--start-date"):
                pass
            elif opt in ("--duration"):
                pass
            elif opt in ("--today"):
                today = True
            elif opt in ("--print-sites"):
                read_sites_file(SITE_FILE_NAME)
                print_sites()
                sys.exit(2)
            elif opt in ("-V"):
                print "TumblrDownloader v" + __version__
                sys.exit(2)

        # Read from standard sites files
        if len(argv) < 1:
            # Try to read from the standard sites file
            read_sites_file(SITE_FILE_NAME)
            for k, v in sites.iteritems():
                readTumblr(k, v, start_item=start, max_items=maxitems, download_dir=target, today=today)
        elif len(argv) == 1:
            # Try to figure out if a tumblr url or a sites file was given
            if argv[0].endswith('tumblr.com'): # URL found
                url = argv[0].rstrip()
                name = url.split('.')[0]
                readTumblr(name, url, start_item=start, max_items=maxitems, download_dir=target, today=today)
            else: # Try to read the sites file
                read_sites_file(argv[0].rstrip())
                for k, v in sites.iteritems():
                    readTumblr(k, v, start_item=start, max_items=maxitems, download_dir=target, today=today)

            print argv[0]
            url = argv[0]
            #name =
            #readTumblr(k, v, start_item=start, max_items=maxitems, target_dir=target, today=today)
        elif site_file != None:
            pass
        elif site != None:
            pass
        else:
            pass
    except getopt.GetoptError:
        usage()
        sys.exit(2)


if __name__ == "__main__":
	main(sys.argv[1:])
