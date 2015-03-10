#!/usr/bin/env python3

import time
import json
import uuid
import requests
import re
import traceback
from ppp_datamodel.communication import Response, Request
from ppp_datamodel import Resource, Sentence, Triple, Missing, List

import tweepy


class StreamWatcherListener(tweepy.StreamListener):

    def __init__(self, api, me):
        self.__api = api
        print(self.__api.me())
        self.me = me
        super(StreamWatcherListener, self).__init__()

    def request(self, request):
        responses = requests.post('http://core.frontend.askplatyp.us',
                data=request.as_json()).json()
        return map(Response.from_dict, responses)

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
        sentence = re.sub(' +', ' ', sentence).strip() # remove multiple spaces
        twittos_list.remove('@' + self.me)
        prefix = '@%s %s ' % (status.author.screen_name, ' '.join(twittos_list))
        r = Request(id='twitter-%s' % uuid.uuid4().hex,
                language='en',
                tree=Sentence(value=sentence))
        responses = (x.tree for x in self.request(r))
        values = [x.value for x in responses if isinstance(x, Resource)]
        if not values:
            self.__api.update_status(prefix + 'No response', status.id)
        else:
            self.__api.update_status(prefix + values[0], status.id)



    def on_error(self, status_code):
        print('An error has occured! Status code = %s' % status_code)
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
