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

class IRHandler(http.server.BaseHTTPRequestHandler):

  key_table = {
    'vizio': {
      'power': 'KEY_POWER',
      'menu': 'KEY_MENU',
      'ch_up': 'KEY_CHANNELUP',
      'ch_down': 'KEY_CHANNELDOWN',
      'vol_up': 'KEY_VOLUMEUP',
      'vol_down': 'KEY_VOLUMEDOWN',
      '1': 'KEY_1',
      '2': 'KEY_2',
      '3': 'KEY_3',
      '4': 'KEY_4',
      '5': 'KEY_5',
      '6': 'KEY_6',
      '7': 'KEY_7',
      '8': 'KEY_8',
      '9': 'KEY_9',
      '0': 'KEY_0',
      'up': 'KEY_UP',
      'down': 'KEY_DOWN',
      'left': 'KEY_LEFT',
      'right': 'KEY_RIGHT',
      'ok': 'KEY_OK',
      'exit': 'KEY_EXIT',
      'input': 'KEY_VIDEO',
    },
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
