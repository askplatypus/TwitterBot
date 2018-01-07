#!/usr/bin/env python3

import json
import re
import string
import traceback
from datetime import datetime

import requests
import tweepy
from babel import Locale
from babel.dates import format_datetime, format_date, format_time
from babel.numbers import format_number, format_decimal
from babel.units import format_unit
from pyld import jsonld

locale = Locale('en')  # TODO: guess locale


def handle_question(sentence):
    response = requests.get('https://qa.askplatyp.us/v0/ask', params={
        'q': sentence,
        'lang': 'und'
    })
    if response.status_code != 200:
        return 'Our system failed, sorry for the troubles.'

    data = jsonld.expand(response.json())
    for root in data:
        for value in root.get('http://www.w3.org/ns/hydra/core#member', []):
            for result in value.get('http://schema.org/result', []):
                context_subject = None
                context_predicate = None
                for k, v in result.get('@reverse', {}).items():
                    context_predicate = from_caml_case(k.replace('http://schema.org/', ''))
                    context_subject = format_element(v[0])
                if context_subject is not None and context_predicate is not None:
                    return 'The {} of {} is {}'.format(
                        context_predicate,
                        context_subject,
                        format_element(result)
                    )
                else:
                    return 'I have found: {}'.format(format_element(result))
    return 'No response'

def format_element(element):
    # literal
    for value in element.get('http://www.w3.org/1999/02/22-rdf-syntax-ns#value', []):
        type = value.get('@type', '')
        val = value.get('@value', '')
        if type == 'http://www.w3.org/2001/XMLSchema#dateTime':
            bc = (val[0] == '-')
            try:
                return format_datetime(datetime.strptime(val, ('-' if bc else '') + '%Y-%m-%dT%H:%M:%SZ'), locale=locale, format='full') + (
                    ' ' + locale.eras['wide'][0] if bc else '')
            except ValueError:
                return val
        elif type == 'http://www.w3.org/2001/XMLSchema#date':
            bc = (val[0] == '-')
            try:
                return format_date(datetime.strptime(val, ('-' if bc else '') + '%Y-%m-%dZ'), locale=locale, format='full') + (' ' + locale.eras['wide'][0] if bc else '')
            except ValueError:
                return val
        elif type == 'http://www.w3.org/2001/XMLSchema#decimal' or \
                        type == 'http://www.w3.org/2001/XMLSchema#double' or \
                        type == 'http://www.w3.org/2001/XMLSchema#float':
            return format_decimal(float(val), locale=locale)
        elif type == 'http://www.w3.org/2001/XMLSchema#integer':
            return format_number(int(val), locale=locale)
        elif type == 'http://www.w3.org/2001/XMLSchema#time':
            try:
                return format_time(datetime.strptime(val, '%H:%M:%SZ'), locale=locale, format='full')
            except ValueError:
                return val
        else:
            return val

    # entities
    types = element.get('@type', [])

    if 'http://schema.org/GeoCoordinates' in types and \
                    'http://schema.org/latitude' in element and \
                    'http://schema.org/longitude' in element:
        latitude = float(element['http://schema.org/latitude'][0]['@value'])
        longitude = float(element['http://schema.org/longitude'][0]['@value'])
        lat_dir = 'north' if latitude >= 0 else 'south'
        lon_dir = 'east' if longitude >= 0 else 'west'
        return format_unit(abs(latitude), 'angle-degree', locale=locale) + ' ' + lat_dir + ' ' + \
               format_unit(abs(longitude), 'angle-degree', locale=locale) + ' ' + lon_dir
    else:
        for same_as in element.get('http://schema.org/sameAs', []):
            url = same_as.get('@id', same_as.get('@value', ''))
            if url.startswith('http://twitter.com/'):
                return url.replace('http://twitter.com/', '@')
        for name in element.get('http://schema.org/name', []):
            return name.get('@value', '')
    return ''


def from_caml_case(txt):
    return ''.join(' ' + c.lower() if c in string.ascii_uppercase else c for c in txt)


class StreamWatcherListener(tweepy.StreamListener):
    def __init__(self, api, me):
        self.__api = api
        print(self.__api.me())
        self.me = me
        super(StreamWatcherListener, self).__init__()

    def on_status(self, status):
        try:
            self._on_status(status)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            traceback.print_exc()

    def _on_status(self, status):
        twittos_list = re.findall('@[a-zA-Z0-9_]*', status.text)
        sentence = status.text
        for twitto in twittos_list:
            sentence = sentence.replace(twitto, '')
        sentence = re.sub(' +', ' ', sentence).strip()  # remove multiple spaces
        twittos_list.remove('@' + self.me)
        prefix = '@%s %s ' % (status.author.screen_name, ' '.join(twittos_list))
        self.__api.update_status(prefix + handle_question(sentence), status.id)

    def on_error(self, status_code):
        print('An error has occurred! Status code = %s' % status_code)
        return True  # keep stream alive

    def on_timeout(self):
        print('Snoozing Zzzzzz')


def main():
    with open('config.json') as fd:
        config = json.load(fd)

    auth = tweepy.auth.OAuthHandler(
        config['auth']['consumer_key'],
        config['auth']['consumer_secret'])
    auth.set_access_token(
        config['auth']['access_token'],
        config['auth']['access_token_secret'])
    api = tweepy.API(auth)
    me = api.me().screen_name

    stream = tweepy.Stream(auth, StreamWatcherListener(api, me), timeout=None)

    stream.filter(track=[me])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print('Goodbye!')
