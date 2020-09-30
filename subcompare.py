#!/usr/bin/python3

#
# Subdomain Monitoring Tool
# Written by: Cody Skinner
# https://codyskinner.net
# Github: wskinner74
# Twitter: @thecodyskinner
#

import difflib
import json
import requests
import argparse
import os
import configparser

#Argument parsing
parser = argparse.ArgumentParser(description="Track new subdomains")
parser.add_argument("masterFile", help="Master subdomain list")
parser.add_argument("newFile", help="New subdomain list")
parser.add_argument("-d", "--domain", help="Domain to run through sublist3r")
parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
args = parser.parse_args()

#Intro output
if args.verbose:
    print("********************")
    print("subcompare.py")
    print("By: @thecodyskinner")
    print("********************")

#Run sublist3r
if args.domain:
    os.system("sublist3r -d " + args.domain + " -o " + args.newFile)

#Variable setting
config = configparser.ConfigParser()
config.read("config.ini")
read1 = open(args.masterFile)
read2 = open(args.newFile)
lines1 = read1.readlines()
lines2 = read2.readlines()
webhook = config.get("Main", "webhook")
diff = difflib.unified_diff(lines1, lines2, lineterm='', n=0)
lines = list(diff)[2:]
added = [line[1:] for line in lines if line[0] == '+']
removed = [line[1:] for line in lines if line[0] == '-']
subdomains = []
newdomains = 0 

#Check for new entries, ignoring position
for line in added:
    if line not in removed:
        newdomains = 1
        subdomains.append(line)
        addLine = open(args.masterFile, 'a')
        addLine.write(line)
        if args.verbose:
            print(line)
if newdomains != 0:
    if args.verbose:
        print("New subdomains found, pushing to Slack")
    slack_data = 'New Subdomains Found! \n' + ''.join(subdomains)
    response = requests.post(
            webhook, data=json.dumps({'text': slack_data}),
            headers={'Content-Type': 'application/json'}
            )
    if response.status_code != 200:
        raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
                )
