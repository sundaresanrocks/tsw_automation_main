#!/usr/bin/python
#
# Author: Patrick Bailey
# Twitter: @whiteboardoder
#
#The MIT License (MIT)
#
#Copyright (c) 2016 "whiteboardcoder" Patrick Bailey
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
#
######################################

import sys, getopt
import os, cgi, SimpleHTTPServer, SocketServer, logging

PORT = 8080
POST = False


def usage():
  print 'Simple Python HTTP Server'
  print 'Usage [OPTION]\n'
  print '   -p, --port                      Set the port to listen on (default is 8080)'
  print '     , --post <ON/OFF>             Allow Post (Default is OFF; will not overwrite existing file)'
  print ''


class GetHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning(self.headers)
        logging.warning(" =========================================================")
        logging.warning(" =======================    GET   ========================")
        logging.warning(" =========================================================")
        logging.warning(self)
        logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        logging.warning(" =========================================================")
        logging.warning(" ======================= Get Done ========================")
        logging.warning(" =========================================================")


class GetHandlerWithPOST(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning(" =========================================================")
        logging.warning(" =======================    GET   ========================")
        logging.warning(" =========================================================")
        logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        logging.warning(" =========================================================")
        logging.warning(" ======================= Get Done ========================")
        logging.warning(" =========================================================")

    def do_POST(self):
        if(POST):
           logging.warning(" =========================================================")
           logging.warning(" =======================    POST  ========================")
           logging.warning(" =========================================================")
           logging.warning(self.headers)


           # Check if path is there.
           if self.path:

               # Get length of the data and read it.
               length = self.headers['content-length']
               data = self.rfile.read(int(length))

               if(self.path == "/"):
                  self.send_response(500, self.path + ' invalid')
                  logging.warning("500: Invalid path " + self.path + "\n")
               elif(not os.path.exists(os.getcwd() + self.path)):
                  # Write the data to a file in current dir.
                  file = open(os.getcwd() + self.path, 'wb')
                  logging.warning("201: Creating File [" + str(os.getcwd() + self.path) + "]")
                  logging.warning("Sent Data:\n" + data + "\n")
                  file.write(data)
                  file.close()
                  self.send_response(201, self.path + ' Created')
               else:
                  #File exists do not overwrite it
                  logging.warning("409: File Already exists\n")
                  self.send_response(409, 'File already exists')

           logging.warning(" =========================================================")
           logging.warning(" ======================= POST Done =======================")
           logging.warning(" =========================================================")
        else:
           logging.error(" POST is not turned on")


def main(argv):
  global PORT
  global POST

  try:
    opts, args = getopt.getopt(argv, "hp:-post:", ["port=", "post="])
  except getopt.GetoptError:
    print 'Error in arguments\n'
    usage()
    sys.exit(1)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt in ("-p", "--port"):
      PORT = int(arg)
    elif opt in ("--post") and arg.upper() == "ON":
      POST = True

  #Start up server
  if(POST):
    Handler = GetHandlerWithPOST
  else:
    Handler = GetHandler

  server = SocketServer.TCPServer(("", PORT), Handler)
  if(POST):
     print "Serving at port: ", PORT, " POST is ON"
  else:
     print "Serving at port: ", PORT, " POST is OFF"

  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print "\nShutting down Server"
    server.shutdown()



if __name__ == "__main__":
  main(sys.argv[1:])
