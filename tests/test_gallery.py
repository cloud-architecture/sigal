# -*- coding:utf-8 -*-

import os
import pytest

from os.path import join
from sigal.gallery import Album, Media, Image, Video, Gallery
from sigal.settings import read_settings

CURRENT_DIR = os.path.dirname(__file__)
SAMPLE_DIR = os.path.join(CURRENT_DIR, 'sample')

REF = {
    'dir1': {
        'title': 'An example gallery',
        'name': 'dir1',
        'thumbnail': 'dir1/test1/thumbnails/11.tn.jpg',
        'subdirs': ['test1', 'test2'],
        'medias': [],
    },
    'dir1/test1': {
        'title': 'An example sub-category',
        'name': 'test1',
        'thumbnail': 'test1/thumbnails/11.tn.jpg',
        'subdirs': [],
        'medias': ['11.jpg', 'archlinux-kiss-1024x640.png',
                   'flickr_jerquiaga_2394751088_cc-by-nc.jpg'],
    },
    'dir1/test2': {
        'title': 'Test2',
        'name': 'test2',
        'thumbnail': 'test2/thumbnails/21.tn.jpg',
        'subdirs': [],
        'medias': ['21.jpg', '22.jpg'],
    },
    'dir2': {
        'title': 'Another example gallery with a very long name',
        'name': 'dir2',
        'thumbnail': 'dir2/thumbnails/m57_the_ring_nebula-587px.tn.jpg',
        'subdirs': [],
        'medias': ['exo20101028-b-full.jpg',
                   'm57_the_ring_nebula-587px.jpg',
                   'Hubble ultra deep field.jpg',
                   'Hubble Interacting Galaxy NGC 5257.jpg'],
    },
    u'accentué': {
        'title': u'Accentué',
        'name': u'accentué',
        'thumbnail': u'accentué/thumbnails/hélicoïde.tn.jpg',
        'subdirs': [],
        'medias': [u'hélicoïde.jpg', 'superdupont_source_wikipedia_en.jpg'],
    },
    'video': {
        'title': 'Video',
        'name': 'video',
        'thumbnail': 'video/thumbnails/stallman software-freedom-day-low.tn.jpg',
        'subdirs': [],
        'medias': ['stallman software-freedom-day-low.ogv']
    }
}


@pytest.fixture(scope='module')
def settings():
    """Read the sample config file."""
    return read_settings(os.path.join(SAMPLE_DIR, 'sigal.conf.py'))


def test_media(settings):
    m = Media('11.jpg', 'dir1/test1', settings)
    path = join('dir1', 'test1')
    file_path = join(path, '11.jpg')
    thumb = join('thumbnails', '11.tn.jpg')

    assert m.filename == '11.jpg'
    assert m.file_path == file_path
    assert m.src_path == join(settings['source'], file_path)
    assert m.dst_path == join(settings['destination'], file_path)
    assert m.thumb_name == thumb
    assert m.thumb_path == join(settings['destination'], path, thumb)

    assert repr(m) == "<Media>('{}')".format(file_path)
    assert str(m) == file_path


def test_media_orig(settings):
    settings['keep_orig'] = False
    m = Media('11.jpg', 'dir1/test1', settings)
    assert m.big is None

    settings['keep_orig'] = True
    m = Media('11.jpg', 'dir1/test1', settings)
    assert m.big == 'original/11.jpg'


def test_image(settings, tmpdir):
    settings['destination'] = str(tmpdir)
    m = Image('11.jpg', 'dir1/test1', settings)
    assert m.exif['datetime'] == u'Sunday, 22. January 2006'

    os.makedirs(join(settings['destination'], 'dir1', 'test1', 'thumbnails'))
    assert m.thumbnail == join('thumbnails', '11.tn.jpg')
    assert os.path.isfile(m.thumb_path)


def test_video(settings, tmpdir):
    settings['destination'] = str(tmpdir)
    m = Video('stallman software-freedom-day-low.ogv', 'video', settings)
    file_path = join('video', 'stallman software-freedom-day-low.webm')
    assert m.file_path == file_path
    assert m.dst_path == join(settings['destination'], file_path)

    os.makedirs(join(settings['destination'], 'video', 'thumbnails'))
    assert m.thumbnail == join('thumbnails',
                               'stallman software-freedom-day-low.tn.jpg')
    assert os.path.isfile(m.thumb_path)


@pytest.mark.parametrize("path,album", REF.items())
def test_album(path, album, settings, tmpdir):
    settings['destination'] = str(tmpdir)
    gal = Gallery(settings, ncpu=1)
    a = Album(path, settings, album['subdirs'], album['medias'], gal)

    assert a.title == album['title']
    assert a.name == album['name']
    assert a.subdirs == album['subdirs']
    assert a.thumbnail == album['thumbnail']
    assert [m.filename for m in a.medias] == album['medias']


def test_gallery(settings, tmpdir):
    "Test the Gallery class."

    settings['destination'] = str(tmpdir)
    gal = Gallery(settings, ncpu=1)
    gal.build()

    out_html = os.path.join(settings['destination'], 'index.html')
    assert os.path.isfile(out_html)

    with open(out_html, 'r') as f:
        html = f.read()

    assert '<title>Sigal test gallery</title>' in html
