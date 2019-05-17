#!/usr/bin/env python3

import click
import time
import wxrfile

import os
import datetime
import hashlib
import re
import sys
from ruamel.yaml import YAML  # import yaml

yaml = YAML()
yaml.default_flow_style = False


def check_post_attachments(post: dict, allattach: dict):
    # Scan HTML body for <img> tags, presuming we'll download these
    if re.search(r'<img\s', post.get('body')):
        post['hugo_has_attachments'] = True
    # Also check for attachments known to Wordpress
    if [p for p in allattach if p.get('post_parent') == post.get('post_id')]:
        post['hugo_has_attachments'] = True
    return


def make_post_destinations(post: dict):
    post_date = post.get('post_date', datetime.datetime(1970, 1, 1, 0, 0, 0))
    fn = '{}-{}'.format(
        post_date.strftime('%Y-%m-%d'), post.get('post_name', 'UNTITLED'))
    if post.get('hugo_has_attachments'):
        filepath = os.path.join('posts', fn, 'index.md')
        bundlepath = os.path.join('posts', fn)
    else:
        filepath = os.path.join('posts', fn + '.md')
        bundlepath = None
    post['hugo_filepath'] = filepath
    post['hugo_bundlepath'] = bundlepath
    post['hugo_uniqueid'] = hashlib.md5(filepath.encode('utf-8')).hexdigest()
    return


def make_post_frontmatter(post):
    front_matter = {
        'title': post.get('title'),
        'date': post.get('post_date').isoformat(),
        'lastmod': post.get('post_date').isoformat(),
        'slug': post.get('post_name', 'UNTITLED'),
        'type': 'post',
    }
    if post.get('excerpt'):
        front_matter['summary'] = post.get('excerpt')
    if post.get('author'):
        # front_matter['author'] = post.get('author')
        front_matter['author'] = 'Scott Johnston'
    if post.get('categories'):
        front_matter['categories'] = post.get('categories')
    if post.get('tags'):
        front_matter['tags'] = post.get('tags')
    if post.get('status') == 'draft':
        front_matter['draft'] = True
    post['hugo_front_matter'] = front_matter
    return


def convert_post(post: dict):
    #click.echo('converting {}'.format(post.get('title')))
    #make_post_filename(post)
    #click.echo(f)
    return


@click.command()
@click.argument('wxr_file', type=click.Path(exists=True))
def main(wxr_file):
    """Convert a Wordpress WXR export to a Hugo site."""
    click.echo('Reading file {}...'.format(wxr_file))
    w = wxrfile.WXRFile(wxr_file)
    all_posts = w.get_posts()[:13]
    all_attachments = w.get_attachments()

    with click.progressbar(
            all_posts, label='Munching metadata.....', show_pos=True) as bar:
        for post in bar:
            check_post_attachments(post, all_attachments)
            make_post_destinations(post)
            make_post_frontmatter(post)

    with click.progressbar(
            all_posts, label='Processing posts......', show_pos=True) as bar:
        for post in bar:
            convert_post(post)
    with click.progressbar(
            all_posts, label='Adding attachments....', show_pos=True) as bar:
        for post in bar:
            pass
    with click.progressbar(
            range(0, 10), label='Converting comments...',
            show_pos=True) as bar:
        for user in bar:
            pass
    for post in all_posts:
        print('Post {}'.format(post.get('title')))
        print('... file {}'.format(post.get('hugo_filepath')))
        print('... pubDate   {}'.format(post.get('pubDate')))
        print('... post_date {}'.format(post.get('post_date').isoformat()))
        print('... post_gmt  {}'.format(post.get('post_date_gmt').isoformat()))
        yaml.dump(post.get('hugo_front_matter'), sys.stdout)


# delete me
if __name__ == '__main__':
    main()
