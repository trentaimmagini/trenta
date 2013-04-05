#!/usr/bin/python

from quopri import decodestring
import sys

ip2server = {}
server2ip = {}
title2ip  = {}

for line in sys.stdin:
    try:
      ip, ts, code, record = line.split()
    except:
      continue
    for line in decodestring(record).split('\n'):
        if line.startswith('Server: '):
            server = line.split(':',1)[1].strip()
            ip2server.setdefault(ip,set()).add( server )
            server2ip.setdefault(server,set()).add( ip )
        if '<title>' in line or '<TITLE>' in line:
            title = line.strip()
            title2ip.setdefault(title,set()).add(ip)

print "%s unique server lines in %s IPs" % (len(server2ip), len(ip2server))

sortd = lambda d: [ v for v in sorted(d, key=lambda v:len(d[v]), reverse=True ) ]

#for ip in ip2server:
#  if len(ip2server[ip])>1:
#    print ip, ip2server[ip]

print "-- titles:"
for title in sortd(title2ip):
  print "%s (%s)" % (title, len(title2ip[title]))

print "-- server strings:"
for server in sortd(server2ip):
  print "%s (%s)" % (server, len(server2ip[server]))
