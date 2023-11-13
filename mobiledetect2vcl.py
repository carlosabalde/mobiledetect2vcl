#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Mobile Detect => VCL
====================

Please, check out https://github.com/carlosabalde/mobiledetect2vcl
for a detailed description and other useful information.

:copyright: (c) 2014 by Carlos Abalde <carlos.abalde@gmail.com>.
:license: GPL, see LICENSE.txt for more details.
'''


import sys
import re
import argparse
import urllib.request, urllib.error, urllib.parse
import json
import datetime

LOCATION = 'https://raw.github.com/serbanghita/Mobile-Detect/master/Mobile_Detect.json'
CATEGORIES = ['phones', 'tablets', 'os', 'browsers', 'utilities']
SUBROUTINE = 'mobile_detect'
CATEGORY = 'X-Mobile-Category'
TYPE = 'X-Mobile-Type'
TIMEOUT = 30


def load(location):
    '''Loads & parses Mobile Detect JSON database (URL or file path).

    '''
    if re.match(r'^https?://', location):
        fp = urllib.request.urlopen(location, {}, TIMEOUT)
        assert(fp.getcode() == 200)
    else:
        fp = open(location, 'r')
    result = json.load(fp)
    fp.close()
    return result


def main(location, subroutine_name, category_header, type_header):
    # Load JSON database.
    db = load(location)

    # Build rules.
    rules = []
    for category in CATEGORIES:
        for type, regexp in list(db['uaMatch'].get(category, {}).items()):
            if isinstance(regexp, list):
                regexp = '|'.join(regexp)
            rule = '(req.http.User-Agent ~ {"(?U)%s"}) {\n' % regexp
            rule += '\t\tset req.http.%(header)s = "%(value)s";\n' % {
                'header': category_header,
                'value': category,
            }
            rule += '\t\tset req.http.%(header)s = "%(value)s";\n' % {
                'header': type_header,
                'value': type,
            }
            rules.append(rule)

    # Dump VCL.
    if len(rules) > 0:
        sys.stdout.write('''##
## Automatically generated by mobiledetect2vcl on %(date)s.
##
## Input:     req.http.User-Agent
##
## Output:    req.http.%(category_header)s (%(categories)s)
##            req.http.%(type_header)s
##
## Generator: https://github.com/carlosabalde/mobiledetect2vcl
## Database:  %(location)s
## Version:   %(version)s
##

sub %(subroutine)s {
\tunset req.http.%(category_header)s;
\tunset req.http.%(type_header)s;

\tif %(rules)s \t}
}
''' % {
            'date': datetime.datetime.now().strftime('%b %d %Y %H:%M:%S'),
            'subroutine': subroutine_name,
            'category_header': category_header,
            'type_header': type_header,
            'categories': ', '.join(CATEGORIES),
            'location': location,
            'version': db['version'],
            'rules': '\t} elsif '.join(rules),
        })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--location', dest='location', type=str, required=False,
        default=LOCATION,
        help='location (URL or file path) of the Mobile Detect JSON '
             'database (see https://github.com/serbanghita/Mobile-Detect)')

    parser.add_argument(
        '--sub', dest='subroutine', type=str, required=False,
        default=SUBROUTINE,
        help='name of the mobile detection VCL subroutine to be generated')

    parser.add_argument(
        '--cat', dest='category', type=str, required=False,
        default=CATEGORY,
        help='name of the HTTP header in the \'req\' object where the mobile '
             'category (\'phones\', \'tables\', etc.) will be stored')

    parser.add_argument(
        '--type', dest='type', type=str, required=False,
        default=TYPE,
        help='name of the HTTP header in the \'req\' object where the mobile '
             'type (\'iPhone\', \'BlackBerry\', etc.) will be stored')

    options = parser.parse_args()

    main(
        options.location.strip(),
        options.subroutine.strip(),
        options.category.strip(),
        options.type.strip())
