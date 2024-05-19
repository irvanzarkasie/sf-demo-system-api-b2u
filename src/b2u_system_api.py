import sys
import json
from flask import Flask, request, jsonify, make_response, Response
import pprint
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import uuid
import socket
from datetime import datetime, timedelta
import os
import urllib3
from lxml import etree as ET

app = Flask(__name__)

# CONSTANTS
api_host = socket.gethostname()
api_port = 35020
api_id = "b2u_system_api"

# Work directory setup
script_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = "/".join(script_dir.split("/")[:-1])
log_dir = "{home_dir}/logs".format(home_dir=home_dir)

# HTTP connection pool
http = urllib3.PoolManager()

@app.route('/sys/b2u/booking/routes', methods=['GET'])
def getRoutes():
  # Parse arguments
  args = request.args
  departure_code = args.get("departure_code", "")
  destination_code = args.get("destination_code", "")

  data = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://www.example.org/Bookings/">
   <soapenv:Header/>
   <soapenv:Body>
      <tns:getRoutes>
         <tns:departureCode></tns:departureCode>
         <tns:destinationCode></tns:destinationCode>
      </tns:getRoutes>
   </soapenv:Body>
</soapenv:Envelope>
  """
  resp = http.request("POST", "http://168.119.225.15:38000/getRoutes", body=data, headers={'Content-Type': 'application/xml'})
  xmlpayload = ET.fromstring(resp.data.decode("utf-8"))

  ns = {"book": "http://www.example.org/Bookings/"}

  for node in xmlpayload.xpath("//book:getRoutesResponse/routes", namespaces=ns):
    print(node.xpath("//departureCode/text()"))
    print(node.xpath("//destinationCode/text()"))
  # end for
  
  return jsonify({})
# end def

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=api_port)
# end if