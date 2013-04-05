import sys
import urlparse
import logging
import csv
import json
csv.field_size_limit(1000000000)


"""
Given a CSV file with lines of form "<ip>,<HTTP response>, <HTTP
headers>", see if we recognize the camera, and for each camera we
recognize we spit out the resource URL in json.

For example, given:
http://128.171.104.32/
you get back
http://128.171.104.32/mjpg/video.mjpg

The results of this script are supposed to be fed to the anopticon.
"""

def gatherer_axis(url):
    """
    In AXIS cameras, if you append "mjpg/video.mjpg" to the root URL, you get a cgi stream or something.

    Example: http://128.171.104.32/mjpg/video.mjpg
    """
    root_url = "http://" + urlparse.urlparse(url).path + "/mjpg/video.mjpg"
    logging.debug("Found AXIS (%s): %s" % (url, root_url))
    return "%s" % root_url

def gatherer_panasonic(url):
    """
    In Panasonic cameras, if you append "nphMotionJpeg?Resolution=640x480&Quality=Standard" you get the resource

    Example: http://61.119.240.67/nphMotionJpeg?Resolution=640x480&Quality=Standard
    """
    root_url = "http://" + urlparse.urlparse(url).path + "/nphMotionJpeg?Resolution=640x480&Quality=Standard"
    logging.debug("Found Panasonic (%s): %s" % (url, root_url))
    return "%s" % root_url

def gatherer_edimax(url):
    """
    In EDIMAx cameras, if you append "mjpg/video.mjpg" to the root URL, you get a cgi stream or something.

    Example: http://84.41.73.48:8080/default.asp
    """
    root_url = "http://" + urlparse.urlparse(url).path + "/mjpg/video.mjpg"
    logging.debug("Found EDIMAX (%s): %s" % (url, root_url))
    return "%s" % root_url

def gatherer_mobotix(url):
    """
    In EDIMAx cameras, if you append "mjpg/video.mjpg" to the root URL, you get a cgi stream or something.

    Example: http://84.41.73.48:8080/default.asp
    """
    root_url = "http://" + urlparse.urlparse(url).path + "/mjpg/video.mjpg"
    logging.debug("Found MOBOTIX (%s): %s" % (url, root_url))
    return "%s" % root_url

def gatherer_axis_2100(url):
    root_url = "http://" + urlparse.urlparse(url).path + "/cgi-bin/fullsize.jpg?motion=0&dummy=1364964764297"
    logging.debug("Found AXIS 2100 (%s): %s" % (url, root_url))
    return "%s" % root_url

def gatherer_webcamxp(url):
    root_url = "http://" + urlparse.urlparse(url).path + "/cam_1.cgi"
    logging.debug("Found Webcam XP (%s): %s" % (url, root_url))
    return "%s" % root_url

def detector_axis_2100(homepage):
    """Return True if this is the homepage of an AXIS camera."""

    if "AXIS 2100 Network Camera" in homepage:
        return True

    return False

def detector_generic_axis(homepage):
    """Return True if this is the homepage of an AXIS camera."""

    if "AXIS" in homepage and "Camera" in homepage:
        return True

    if 'CONTENT="0; URL=/view/' in homepage:
        return True

    return False

def detector_panasonic(homepage):
    if "<TITLE>Network Camera </TITLE>" in homepage:
        return True

    if "CgiTagMenu?" in homepage:
        return True

    return False

def detector_edimax(homepage):
    if "Internet MPEG-4 Pan/Tilt Camera" in homepage:
        return True

    return False

def detector_mobotix(homepage):
    if "/cgi-bin/guestimage.html" in homepage:
        return True

    return False


def detector_webcamxp(homepage):
    if "webcams and ip cameras server for windows" in homepage:
        return True

    return False

def usage():
    print "Usage: %s <webcam_urls_file>" % (sys.argv[0])
    sys.exit(1)

def resorcery():
    list_of_urls = []

    if len(sys.argv) != 2:
        usage()

    with open(sys.argv[1], 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if not row:
                continue

            host = row[0]
            try:
              response = row[1]
              headers = row[2]
            except IndexError:
              try:
                error = row[1]
              except:
                pass
              continue

#            headers = row[2]

            # Download the page and run our detectors on it.
            logging.debug("About to run our gatherers on %s with %s" % (host,response))

            # The plan is to pass the HTTP payload to the
            # webcam-specific detectors, and then pass the URL to our
            # resource gatheres to get the resouce URL out of them.

            # XXX What about http://101.1.219.71/viewer/live/en/live.html ?

            if detector_axis_2100(response):
                list_of_urls.append(gatherer_axis_2100(host))
            elif detector_generic_axis(response):
                list_of_urls.append(gatherer_axis(host))
            elif detector_webcamxp(response):
                list_of_urls.append(gatherer_webcamxp(host))
            elif detector_panasonic(response):
                list_of_urls.append(gatherer_panasonic(host))
            elif detector_edimax(response):
                list_of_urls.append(gatherer_edimax(host))
            elif detector_mobotix(response):
                list_of_urls.append(gatherer_mobotix(host))
            else:
                continue

        print json.dumps(list_of_urls)

if __name__ == '__main__':
    logger = logging.getLogger('')
    logger.setLevel(logging.WARNING)
    resorcery()
