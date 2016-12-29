#!/usr/bin/python3

import http.server
import logging
import os
import shlex
import shutil
import sys
import subprocess

from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

PORT = 8000

def _generate_mapping(*args, **kargs):
  mapping = dict((name, 'KEY_' + name.upper()) for name in args)
  mapping.update(kargs)
  return mapping

class IRHandler(http.server.BaseHTTPRequestHandler):

  key_table = {
      'vizio': _generate_mapping(
        'power', 'menu', 'mute', 'ok', 'exit', 'info',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'up', 'down', 'left', 'right',
        'stop', 'play', 'pause', 'forward', 'rewind',
        'subtitle',

        ch_up='KEY_CHANNELUP',
        ch_down='KEY_CHANNELDOWN',
        vol_up='KEY_VOLUMEUP',
        vol_down='KEY_VOLUMEDOWN',
        input='KEY_VIDEO',
        apps='KEY_PROGRAM',
        amazon='KEY_PROG1',
        ),
  }

  def do_GET(self):
    if '/' == self.path:
      self.send_html('irctl.html')
    elif self.path.startswith('/remote?'):
      qs = parse_qs(urlparse(self.path).query)
      if not qs['key'] or not qs['name']:
        logging.error('invalid argument')
        self.send_error(HTTPStatus.BAD_REQUEST, 'Invalid argument')
        return

      remote_name = qs['name'][0]
      key = qs['key'][0]
      if (remote_name not in IRHandler.key_table or
          key not in IRHandler.key_table[remote_name]):
        logging.error('unknown key "%s" on remote %s"' % (
          key, remote_name))
        self.send_error(HTTPStatus.NOT_FOUND, 'Unrecognized key')
        return

      try:
        subprocess.call(
            'irsend SEND_ONCE %s %s' % (
              remote_name, IRHandler.key_table[remote_name][key]),
            shell=True)
      except OSError as e:
        logging.error('irsend failed: ', e)
      self.send_response(HTTPStatus.NO_CONTENT)
      self.end_headers()
    else:
      self.send_error(HTTPStatus.NOT_FOUND, 'Not found')

  def send_html(self, filepath):
    self.send_response(HTTPStatus.OK)
    self.send_header('Content-type', 'text/html')
    self.send_header('Content-Length', str(os.stat(filepath)[6]))
    self.end_headers()
    with open(filepath, 'rb') as f:
      shutil.copyfileobj(f, self.wfile)

httpd = http.server.HTTPServer(('', PORT), IRHandler)
print('irhttpd now serving at port', PORT)

try:
  httpd.serve_forever()
except KeyboardInterrupt:
  print("\nKeyboard interrupt received, exiting.")
  httpd.server_close()
  sys.exit(0)
