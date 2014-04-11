#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import sys

import argparse
import dateutil.parser

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
import libtaxii.clients as tc


def main():
    parser = argparse.ArgumentParser(description="Poll Client")
    parser.add_argument("--host", dest="host", default="localhost", help="Host where the Poll Service is hosted. Defaults to localhost.")
    parser.add_argument("--port", dest="port", default="8080", help="Port where the Poll Service is hosted. Defaults to 8080.")
    parser.add_argument("--path", dest="path", default="/services/query_example/", help="Path where the Poll Service is hosted. Defaults to /services/query_example/.")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection to poll. Defaults to 'default'.")
    parser.add_argument("--ip", dest="ip", default=None, help="The IP address to query")
    parser.add_argument("--hash", dest="hash", default=None, help="The file hash to query")

    args = parser.parse_args()
    
    if args.ip is None and args.hash is None:
        print "At least one of --ip or --hash must be specified!"
        sys.exit()
    
    criterion = []
    
    if args.ip is not None:
        tmp = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE,
                                              relationship='equals',
                                              parameters={'value': args.ip, 'match_type': 'case_insensitive_string'})
        criterion.append(tdq.DefaultQuery.Criterion(target='//Address_Value', test=tmp))
    
    if args.hash is not None:
        tmp = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE,
                                              relationship='equals',
                                              parameters={'value': args.hash, 'match_type': 'case_insensitive_string'})
        criterion.append(tdq.DefaultQuery.Criterion(target='//Hash/Simple_Hash_Value', test=tmp))
    
    criteria = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=criterion)
    
    q = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria)

    poll_req = tm11.PollRequest(message_id=tm11.generate_message_id(),
                              collection_name=args.collection,
                              poll_parameters=tm11.PollRequest.PollParameters(query=q))

    poll_req_xml = poll_req.to_xml()
    print "Poll Request: \r\n", poll_req_xml
    client = tc.HttpClient()
    client.setProxy('noproxy') 
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml()

if __name__ == "__main__":
    main()
