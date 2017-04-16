#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'TC Team'
SITENAME = u'Town Crier'

SITEURL = 'http://www.town-crier.org/staging/'
THEME = './themes/semantic-ui'
PATH = 'content'
TIMEZONE = 'America/New_York'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

MENU_LINKS = [
('What is TC', 'what-is-tc.html'),
('Get Started', 'get-started.html'),
('Dev', 'dev.html'),
('Research', 'research.html'),
('FAQ', 'faq.html'),
]

LOGOPATH = '/theme/images/logo-tc.png'

LINKS = [
    ('Ethereum Project', 'https://www.ethereum.org/'),
    ]

GOOGLE_ANALYTICS='UA-72748416-5'
DISQUS_SITENAME = 'town-crier'
