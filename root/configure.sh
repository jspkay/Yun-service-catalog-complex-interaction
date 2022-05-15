#!/bin/sh

#Installing python3
opkg update 
opkg install python3-light

ln -sf /usr/bin/python3 /usr/bin/python # make python the alias for python3

#other dependencies for paho
opkg install python3-codecs python3-logging

#dependencies for requests
opkg install python3-cgi # includes also email
