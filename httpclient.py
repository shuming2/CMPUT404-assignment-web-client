#!/usr/bin/env python
# coding: utf-8
# Copyright 2017 Shuming Zhang
# Based on code from Abram Hindle,
# https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

#
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    # def __str__(self):
    #     return str(self.code) + "\n" + self.body

class HTTPClient(object):
    def get_host_port(self,url):
        return urlparse.urlparse(url)

    def connect(self, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not port:
            port = 80
        clientSocket.connect((host, port))
        return clientSocket

    def get_code(self, data):
        code = data.split()[1]
        return int(code)

    # ?
    def get_headers(self,data):
        return None

    def get_body(self, data):
        i = data.find("\r\n\r\n")
        if len(data) == i+4:
            body = None
        else:
            body = data[i+4:]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        parse = self.get_host_port(url)
        hostname = parse.hostname
        port = parse.port
        path = parse.path
        if path == "":
            path = "/"

        clientSocket = self.connect(hostname, port)

        clientSocket.sendall("GET " + path + " HTTP/1.0\r\n" +
                             "Host: " + hostname + "\r\n" +
                             "Accept: */*\r\n" +
                             "\r\n")

        response = self.recvall(clientSocket)
        print response
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        parse = self.get_host_port(url)
        hostname = parse.hostname
        port = parse.port
        path = parse.path
        if path == "":
            path = "/"

        # Convert arguments to urlencoded string
        content = ""
        if args:
            content = urllib.urlencode(args)

        clientSocket = self.connect(hostname, port)

        clientSocket.sendall("POST " + path + " HTTP/1.0\r\n" +
                             "Host: " + hostname + "\r\n" +
                             "Accept: */*\r\n" +
                             "Content-Length: " + str(len(content)) + "\r\n" +
                             "Content-Type: application/x-www-form-urlencoded\r\n" +
                             "\r\n" +
                             content
                             )

        response = self.recvall(clientSocket)
        print response
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
