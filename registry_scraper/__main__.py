#!/usr/bin/env python

import argparse
import os

from pprint import pprint

from scraper import Scraper, _split_image_and_tag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=str, nargs='+',
                        help="Name of image to scrape."
                             " Don't include registry name."
                             " eg. myimage:mytag. Tag defaults to latest")
    parser.add_argument('-s', '--storage-type', type=str,
                        choices=['local', 's3'],
                        default='local',
                        help="Registry storage backend.")
    parser.add_argument('-d', '--data-dir', type=str, default='data',
                        help="Registry data directory or S3 bucket")
    parser.add_argument('-o', '--output-dir', type=str, default='data-copy',
                        help="Path to copy to")
    parser.add_argument('-c', '--check', dest='check', action='store_true',
                        help="Only check files, don't download them")
    parser.add_argument('--no-check', dest='check', action='store_false',
                        help="Download files, don't just check them")
    parser.set_defaults(check=False)

    args = parser.parse_args()

    scraper = Scraper(args.storage_type, args.data_dir)
    paths = set()
    for img in args.image:
        image, tag = _split_image_and_tag(img)
        paths.update(scraper.get_paths(image, tag))
    pprint(paths)
    if args.check:
        scraper.check_paths(paths)
        print("Image(s) {} successfully checked".format(args.image))
    else:
        scraper.copy_paths(paths, args.output_dir)


if __name__ == '__main__':
    main()
