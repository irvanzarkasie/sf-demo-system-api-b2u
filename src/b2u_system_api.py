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

# Hash map for departure/destination code
DEPDESTCODEMAP = {
  "MY-Z1001": "MY-01",
  "MY-Z1002": "MY-02",
  "SG-S1001": "SG-01",
  "SG-S1002": "SG-02"
}

@app.route('/sys/b2u/booking/routes', methods=['GET'])
def getRoutes():
  # Parse arguments
  args = request.args
  departure_code = args.get("departureCode", None)
  destination_code = args.get("destinationCode", None)

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

  resp_list = []
  for node in xmlpayload.xpath("//book:getRoutesResponse/routes", namespaces=ns):
    dep_code = node.findtext("departureCode")
    dest_code = node.findtext("destinationCode")
    mapped_dep_code = DEPDESTCODEMAP.get(dep_code, "")
    mapped_dest_code = DEPDESTCODEMAP.get(dest_code, "")
    
    print("departureCode", departure_code)
    print("mapped_dep_code", mapped_dep_code)

    print("destinationCode", destination_code)
    print("mapped_dest_code", mapped_dest_code)

    if departure_code is not None and destination_code is not None:
      if departure_code == mapped_dep_code and destination_code == mapped_dest_code:
        resp_list.append({
          "departureCode": mapped_dep_code,
          "destinationCode": mapped_dest_code
        })
      # end if
    # end if
    elif departure_code is not None and destination_code is None:
      if departure_code == mapped_dep_code:
        resp_list.append({
          "departureCode": mapped_dep_code,
          "destinationCode": mapped_dest_code
        })
      # end if
    # end if
    elif departure_code is None and destination_code is not None:
      if destination_code == mapped_dest_code:
        resp_list.append({
          "departureCode": mapped_dep_code,
          "destinationCode": mapped_dest_code
        })
      # end if
    # end if
    else:
      resp_list.append({
        "departureCode": mapped_dep_code,
        "destinationCode": mapped_dest_code
      })
    # end else
  # end for
  
  return jsonify(resp_list)
# end def

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=api_port)
# end if