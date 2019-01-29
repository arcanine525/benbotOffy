import logging
import hangups

from utils import unicode_to_ascii
import urllib.request

import plugins

import requests
# logger = logging.getLogger(__name__)


def _initialise(bot):
    plugins.register_user_command(["offycauses", "offypr", "getweather"])


def offycauses(bot, event, *args):
    """Offy Causes"""

    htmlmessage = _('Here is a video for Offy Causes<br />')
    htmlmessage += _('<b>{https://www.youtube.com/watch?v=J5g2QSwfvbA}</b>:<br />')

#    logger.debug("{0} ({1}) has requested to lookup '{2}'".format(event.user.full_name, event.user.id_.chat_id, keyword))

    yield from bot.coro_send_message(event.conv, htmlmessage)


def offypr(bot, event, *args):
    """Offy PR Process"""

    htmlmessage = _('PR Process<br />')
    htmlmessage += _('<b>https://docs.google.com/document/d/19djlS_ct9vGGTlnHbvV2RA94d43qBDd_pwGdEIIJewg</b>:<br />')

#    logger.debug("{0} ({1}) has requested to lookup '{2}'".format(event.user.full_name, event.user.id_.chat_id, keyword))

    yield from bot.coro_send_message(event.conv, htmlmessage)


def getweather(bot, event, *args):
    # GET weather from darksky.net
    api_key = '12fdc38699c4a4cd6e6b0eab9c077782'
    offy_latitude = '10.775228'
    offy_longitude = '106.670371'
    
    url = 'https://api.darksky.net/forecast/'+api_key + \
        "/" + offy_latitude + "," + offy_longitude
    req = requests.get(url).json()
    htmlmessage = _('Today weather: <br />')
    htmlmessage += _('-----------------------------------------<br />')
    htmlmessage += _('<b>{}</b><br />').format(str(req['hourly']['summary']))
    htmlmessage += _('-----------------------------------------<br />')
    htmlmessage += _('For more details: <br />')
    htmlmessage += _('<b>https://darksky.net/forecast/10.7752,106.6704/si12/en</b><br />')

    yield from bot.coro_send_message(event.conv, htmlmessage)

