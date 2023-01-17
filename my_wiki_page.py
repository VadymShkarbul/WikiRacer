import time

import wikipedia
from typing import List

from bs4 import BeautifulSoup
from wikipedia import PageError, ODD_ERROR_MESSAGE, RedirectError, DisambiguationError
from wikipedia.wikipedia import _wiki_request

# TODO: Check this before proceed!!!
"""

except wikipedia.exceptions.DisambiguationError as e:
            links = e.options[:200] what this code do?
This code is handling a specific exception that may occur when trying to access a Wikipedia page, the wikipedia.exceptions.DisambiguationError.

Sometimes, when you try to access a Wikipedia page, the page title may refer to multiple pages with different subjects (e.g 'Apple' could refer to the fruit or the company). When this happens, Wikipedia returns a disambiguation page, which lists the different pages that the title could refer to.

When this happens, the wikipediaapi library raises a wikipedia.exceptions.DisambiguationError exception, which contains a property options that lists the different pages that the title could refer to.

The code except wikipedia.exceptions.DisambiguationError as e: links = e.options[:200] is catching this exception and getting the first 200 options to handle it.

This way, if a disambiguation page is encountered, the script will take the first 200 options and continue with the algorithm instead of stopping.
"""
class myWikiPage(wikipedia.WikipediaPage):
    def __init__(self, title=None, pageid=None, redirect=True, preload=False, original_title=''):
        super(myWikiPage, self).__init__(title=title, pageid=pageid, redirect=redirect, preload=preload, original_title=original_title)

    def __load(self, redirect=True, preload=False):
        '''
        Load basic information from Wikipedia.
        Confirm that page exists and is not a disambiguation/redirect.

        Does not need to be called manually, should be called automatically during __init__.
        '''
        query_params = {
            'prop': 'info|pageprops',
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'redirects': '',
        }
        if not getattr(self, 'pageid', None):
            query_params['titles'] = self.title
        else:
            query_params['pageids'] = self.pageid

        request = _wiki_request(query_params)

        query = request['query']
        pageid = list(query['pages'].keys())[0]
        page = query['pages'][pageid]

        # missing is present if the page is missing
        if 'missing' in page:
            if hasattr(self, 'title'):
                raise PageError(self.title)
            else:
                raise PageError(pageid=self.pageid)

        # same thing for redirect, except it shows up in query instead of page for
        # whatever silly reason
        elif 'redirects' in query:
            if redirect:
                redirects = query['redirects'][0]

                if 'normalized' in query:
                    normalized = query['normalized'][0]
                    assert normalized['from'] == self.title, ODD_ERROR_MESSAGE

                    from_title = normalized['to']

                else:
                    from_title = self.title

                assert redirects['from'] == from_title, ODD_ERROR_MESSAGE

                # change the title and reload the whole object
                self.__init__(redirects['to'], redirect=redirect, preload=preload)

            else:
                raise RedirectError(getattr(self, 'title', page['title']))

        # since we only asked for disambiguation in ppprop,
        # if a pageprop is returned,
        # then the page must be a disambiguation page
        elif 'pageprops' in page:
            query_params = {
                'prop': 'revisions',
                'rvprop': 'content',
                'rvparse': '',
                'rvlimit': 1
            }
            if hasattr(self, 'pageid'):
                query_params['pageids'] = self.pageid
            else:
                query_params['titles'] = self.title
            request = _wiki_request(query_params)
            html = request['query']['pages'][pageid]['revisions'][0]['*']

            lis = BeautifulSoup(html, features="lxml").find_all('li')
            filtered_lis = [li for li in lis if not 'tocsection' in ''.join(li.get('class', []))]
            may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]

            raise DisambiguationError(getattr(self, 'title', page['title']), may_refer_to)

        else:
            self.pageid = pageid
            self.title = page['title']
            self.url = page['fullurl']


