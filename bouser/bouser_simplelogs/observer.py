# coding: utf-8
from zope.interface import provider, implementer
from twisted.logger import ILogObserver, formatEvent
from twisted.internet import reactor
from twisted.internet.defer import succeed
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.python import log


@implementer(IBodyProducer)
class StringProducer(object):
    def __init__(self, body, jsonify=True):
        from bouser.utils import as_json
        self.body = as_json(body) if jsonify else body
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


@implementer(ILogObserver)
class SimplelogsLogObserver(object):
    """
    Log observer that sends log entry to simplelogs service.
    """
    simplelogs_url = None

    def __init__(self, system_name='Coldstar'):
        self.system_name = system_name

    @classmethod
    def set_url(cls, url):
        cls.simplelogs_url = url.encode('utf-8').rstrip('/') + '/'

    def configure(self, config):
        if 'system_name' in config:
            self.system_name = config['system_name']

    def __call__(self, event):
        """
        Make log entry and send it

        @param event: An event.
        @type event: L{dict}
        """
        if not self.simplelogs_url:
            return

        message = formatEvent(event)
        if "log_failure" in event:
            try:
                traceback = event["log_failure"].getTraceback()
            except Exception:
                traceback = u"(UNABLE TO OBTAIN TRACEBACK FROM EVENT)\n"
            message = u"\n".join((message, traceback))

        level = event['log_level'].name.lower()
        if level == 'warn':
            level = 'warning'
        data = {
            'level': level,
            'owner': {
                'name': self.system_name,
                'version': None
            },
            'data': message,
            'tags': event.get('tags') or []
        }

        self._send(data)

    def _send(self, data):
        """
        Produce http post request with log entry data
        """
        agent = Agent(reactor)
        d = agent.request(
            'POST',
            self.simplelogs_url + 'api/entry/',
            Headers({'User-Agent': ['Twisted Web Client'],
                     'Content-Type': ['application/json']}),
            StringProducer(data)
        )

        def cbBody(body):
            return body

        def cbResponse(response):
            if 200 < response.code or response.code > 299:
                log.msg('Error sending to simplelogs: {0} {1}'.format(
                    response.code, response.phrase).encode('utf-8'))
            d = readBody(response)
            d.addCallback(cbBody)
            return d

        d.addCallback(cbResponse)

        def cbError(failure):
            log.msg('Error sending to simplelogs: {0}'.format(failure))
        d.addErrback(cbError)
