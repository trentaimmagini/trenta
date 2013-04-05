import sys
import csv
import os
import re

from glob import glob
from twisted.internet import defer, reactor, protocol
from twisted.web import client

"""
Given a list of IPs, visit them all and do a GET request. See if the
response contains "webcam" in its headers or payload, and if it does
write it to a CSV file in the format:
<IP address>, <HTTP payload>, <HTTP headers>

The results of this script are supposed to be fed to the resorcerer.
"""

if len(sys.argv) != 3:
  print "usage: %s [input_filename] [output_filename]" % sys.argv[0]
  sys.exit(2)

input_directory = sys.argv[1]
output_filename = sys.argv[2]

output_fp = open(output_filename, 'w+')
csvwriter = csv.writer(output_fp, delimiter=',',
                                  quotechar='|', quoting=csv.QUOTE_MINIMAL)

class Receiver(protocol.Protocol):
    def __init__(self, finished):
      self.finished = finished
      self.data = ''

    def dataReceived(self, bytes):
        self.data += bytes

    def connectionLost(self, reason):
        self.finished.callback(self.data)

def matches_cam(line, headers=None):
  """Search page for 'webcam' in headers or payload."""
  ll = line.lower()
  if headers and 'webcam' in headers.getRawHeaders('Server')[0].lower():
    return ll

  if 'webcam' in ll or \
    'cam' in ll:
    print "line: %s" % ll
    print "Found!"
    return ll
  else:
    return False

class CameraMatcher(object):
  ip = '127.0.0.1'

  def gotBody(self, body):
    if matches_cam(body, self.headers):
      csvwriter.writerow((self.ip, body, str(self.headers)))
    else:
      csvwriter.writerow((self.ip, 'no-match', ''))

  def gotResponse(self, response):
    finished = defer.Deferred()
    response.deliverBody(Receiver(finished))
    print "Completed %s" % response
    self.headers = response.headers
    finished.addCallback(self.gotBody)
    return finished

  def scanit(self, line):
    self.ip = re.match('^((\d+\.){3}\d+)', line).group(1)
    uri = 'http://'+self.ip+'/'
    agent = client.Agent(reactor)
    print "Doing GET request %s" % uri
    d = agent.request('GET', uri)
    d.addCallback(self.gotResponse)
    @d.addErrback
    def errback(error):
      csvwriter.writerow((self.ip, str(error), ''))
    return d

@defer.inlineCallbacks
def start(input_filename, lc):
  i = 0
  items = []
  with open(input_filename) as f:
    for line in f:
      percent = float(i)/float(lc) * 100
      print "%f%%" % percent

      if matches_cam(line):
        matcher = CameraMatcher()
        d = matcher.scanit(line)
        items.append(d)

      if len(items) == 10:
        yield defer.DeferredList(items)
        items = []

      i += 1

  yield defer.DeferredList(items)
  output_fp.close()
  reactor.stop()

def compute_linecount(filename):
  with open(filename) as f:
    lc = len(f.readlines())
  return lc

base_dir = os.path.abspath(input_directory)
input_filename = base_dir
# for input_filename in glob(os.path.join(base_dir, '*TCP*')):
lc = compute_linecount(input_filename)
print "Working on %s (%s lines)" % (input_filename, lc)
start(input_filename, lc)

reactor.run()
