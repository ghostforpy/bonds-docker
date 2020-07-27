#!/usr/bin/env python
"""
    Small example of a library implementing interaction with Moscow Exchange ISS server.

    Version: 1.2
    Developed for Python 2.6

    @copyright: 2016 by MOEX
"""

import urllib.request as urllib2
# import base64
import http.cookiejar as cookielib
import json

import requests as r
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

requests = {
    'history_secs':
    'http://iss.moex.com/iss/history/engines/%(engine)s/markets/%(market)s/boards/%(board)s/securities.json?date=%(date)s'}

requests_history = 'https://iss.moex.com/iss/statistics/engines/stock/currentprices'


class Config:
    def __init__(self, user='', password='', proxy_url='', debug_level=0):
        """ Container for all the configuration options:
            user: username in MOEX Passport to access real-time data and history
            password: password for this user
            proxy_url: proxy URL if any is used, specified as http://proxy:port
            debug_level: 0 - no output, 1 - send debug info to stdout
        """
        self.debug_level = debug_level
        self.proxy_url = proxy_url
        self.user = user
        self.password = password
        self.auth_url = "https://passport.moex.com/authenticate"


class MicexAuth:
    """ user authentication data and functions
    """

    def __init__(self, config):
        self.config = config
        self.cookie_jar = cookielib.CookieJar()
        self.auth()

    def auth(self):
        """ one attempt to authenticate
        """
        if self.config.proxy_url:
            proxy = self.config.proxy_url
        else:
            proxy = None
        req = r.get(self.config.auth_url,
                    auth=HTTPBasicAuth(self.config.user,
                                       self.config.password),
                    proxies=proxy)
        self.cookie_jar = req.cookies
        self.passport = None
        for cookie in self.cookie_jar:
            if cookie.name == 'MicexPassportCert':
                self.passport = cookie
                break
        if self.passport is None:
            print ("Cookie not found!")

    def is_real_time(self):
        """ repeat auth request if failed last time or cookie expired
        """
        if not self.passport or (self.passport and self.passport.is_expired()):
            self.auth()
        if self.passport and not self.passport.is_expired():
            return True
        return False


class MicexISSDataHandler:
    """ Data handler which will be called
    by the ISS client to handle downloaded data.
    """

    def __init__(self, container):
        """ The handler will have a container to store received data.
        """
        self.data = container()

    def do(self):
        """ This handler method should be overridden to perform
        the processing of data returned by the server.
        """
        pass


class MicexISSClient:
    """ Methods for interacting with the MICEX ISS server.
    """

    def __init__(self, config, auth, handler=False, container=False):
        """ Create opener for a connection with authorization cookie.
        It's not possible to reuse the opener used to authenticate because
        there's no method in opener to remove auth data.
            config: instance of the Config class with configuration options
            auth: instance of the MicexAuth class with authentication info
            handler: user's handler class inherited from MicexISSDataHandler
            containet: user's container class
        """
        if config.proxy_url:
            self.opener = urllib2.build_opener(urllib2.ProxyHandler({"http": config.proxy_url}),
                                               urllib2.HTTPCookieProcessor(
                                                   auth.cookie_jar),
                                               urllib2.HTTPHandler(debuglevel=config.debug_level))
        else:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(auth.cookie_jar),
                                               urllib2.HTTPHandler(debuglevel=config.debug_level))
        urllib2.install_opener(self.opener)
        if handler:
            self.handler = handler(container)

# Поиск инструмента по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации.
    def search(self, query):
        if len(query) < 3:
            return False
        url = 'http://iss.moex.com/iss/securities.json?q={}'.format(quote(query))
        res = self.opener.open(url)

        jres = json.load(res)
        jres = jres['securities']['data']
        result = {i[1]: {'id_moex': i[0],
                         'regnumber': i[3],
                         'shortname': i[2],
                         'name': i[4],
                         'emitent': i[8],
                         'primary_boardid': i[14],
                         'isin': i[5]} for i in jres}
        return result

    def specification(self, query):
        url = 'https://iss.moex.com/iss/securities/{}.json'.format(query)
        res = self.opener.open(url)
        result = json.load(res)
        description = result['description']['data']
        result_description = {i[0]: i[2]
                              for i in description if i[0] in ["SECID",
                                                               "NAME",
                                                               "SHORTNAME",
                                                               "ISIN",
                                                               "REGNUMBER",
                                                               "TYPENAME",
                                                               "GROUPNAME",
                                                               "FACEVALUE",
                                                               "TYPE",
                                                               "INITIALFACEVALUE",
                                                               "MATDATE",
                                                               "COUPONFREQUENCY",
                                                               "COUPONPERCENT",
                                                               "COUPONVALUE",
                                                               "COUPONDATE",
                                                               ]}
        boards = result['boards']
        s = self.search(query)[query]
        result_description['primary_boardid'] = s['primary_boardid']
        result_description['emitent'] = s['emitent']
        return result_description, boards

    def get_history(self, url):
        start = 0
        cnt = 1
        result = {}
        while cnt > 0:
            res = self.opener.open(url + '?start=' + str(start))

            jres = json.load(res)
            jhist = jres['history']
            jdata = jhist['data']
            jcols = jhist['columns']
            closeIdxx = jcols.index('LEGALCLOSEPRICE')
            closeIdx = jcols.index('CLOSE')
            trade_dateIdx = jcols.index('TRADEDATE')
            for i in jdata:
                date = i[trade_dateIdx].split('-')[::-1]
                result['.'.join(date)] = i[closeIdx] or i[closeIdxx]
            cnt = len(jdata)
            start += cnt
        return result

    def get_history_securities(self, engine, market, board, date):
        """ Get and parse historical data on all the securities at the
        given engine, market, board
        """
        url = requests['history_secs'] % {'engine': engine,
                                          'market': market,
                                          'board': board,
                                          'date': date}

        # always remember about the 'start' argument to get long replies
        start = 0
        cnt = 1
        while cnt > 0:
            res = self.opener.open(url + '&start=' + str(start))
            jres = json.load(res)

            # the following is also just a simple example
            # it is recommended to keep metadata separately

            # root node with historical data
            jhist = jres['history']

            # node with actual data
            jdata = jhist['data']

            # node with the list of column IDs in 'data' in correct order;
            # it's also possible to use the iss.json=extended argument instead
            # to get all the IDs together with data (leads to more traffic)
            jcols = jhist['columns']
            secIdx = jcols.index('SECID')
            closeIdx = jcols.index('LEGALCLOSEPRICE')
            tradesIdx = jcols.index('NUMTRADES')

            result = []
            for sec in jdata:
                result.append((sec[secIdx],
                               del_null(sec[closeIdx]),
                               del_null(sec[tradesIdx])))
            # we return pieces of received data on each iteration
            # in order to be able to handle large volumes of data
            # and to start data processing without waiting for
            # the complete reply
            # self.handler.do(result)
            cnt = len(jdata)
            start = start + cnt
        return True


def del_null(num):
    """ replace null string with zero
    """
    return 0 if num is None else num


if __name__ == '__main__':
    pass
