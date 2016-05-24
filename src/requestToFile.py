#!/usr/bin/env python

import json
import csv
try:
    import ConfigParser
except:
    import configparser as ConfigParser
import sys
import logging
import logging.config
import argparse
import requests
import xmltodict
import xml
import os
from xml.etree import ElementTree


class RequestToFile:

    def __init__(self, credentials={}):
        """Initialize the instance"""
        self.url = credentials.get('url')
        self.username = credentials.get('username')
        self.password = credentials.get('password')
        self.keepFields = []
        self.discardFields = []
        self.nodesToTraverse = []
        self.logger = self.getLogger()

    def initFromConfigFile(self, filePath):
        """Initializes instance properties from a config file """
        try:
            config = ConfigParser.RawConfigParser()
            # config.read does not raise an error if no file is found, it just returns
            # an empty list.
            if len(config.read(filePath)) < 1:
                self.logger.error(
                    'Exiting.  Could not find configuarion file "%s"' % filePath)
                sys.exit(4)

            self.url = config.get('REQUEST', 'url')
            self.username = config.get('REQUEST', 'username')
            self.password = config.get('REQUEST', 'password')

            keepFields = json.loads(config.get('KEEP_FIELDS', 'fields'))
            discardFields = json.loads(config.get('DISCARD_FIELDS', 'fields'))
            nodesToTraverse = json.loads(config.get('NESTING', 'fields'))
        except ConfigParser.NoSectionError as e:
            self.logger.error('There is an error in the configuration file %s: %s' %
                              filePath, e)
            sys.exit(0)

        for item in keepFields:
            self.addKeepFields(item)

        for item in discardFields:
            self.addDiscardFields(item)

        for item in nodesToTraverse:
            self.addNestingFields(item)

        if self.areBothListsPopulated(self.keepFields, self.discardFields):
            self.logger.error(
                'You cannot have KEEP_FIELDS and DISCARD_FIELDS in your config file.  Exiting.')
            sys.exit(0)
        return self

    def getLogger(self):
        """Grabs a logger instance"""
        logging.config.fileConfig(os.path.join(
            os.path.dirname(__file__), 'logging.conf'))
        return logging.getLogger('requestToFile')

    def fetchDataFromURL(self, printResponseKeys=False):
        """Fetches XML data"""
        try:
            response = requests.get(self.url,
                                    auth=(self.username, self.password), verify=False)
            if response.status_code == 500:
                self.logger.error('%s replied with: %s. Exiting.' % self.url, response.text)
                sys.exit(1)

            data = None
            if self.isXML(response.text):
                self.logger.debug('Response is valid XML')
                data = json.loads(json.dumps(xmltodict.parse(response.text)))
            elif self.isJSON(response.text):
                self.logger.debug('Response is valid JSON')
                data = json.loads(response.text)
            else:
                self.logger.error(
                    'The type of response from the server cannot be determined does not fit the XML or JSON transport type.  Exiting.')
                sys.exit(2)

            for node in self.nodeTraversalGenerator(self.nodesToTraverse):
                try:
                    data = data[node]
                except KeyError as e:
                    self.logger.error('Key "%s" not found in response.  Exiting' % node)
                    sys.exit(3)

            if printResponseKeys:
                self.printResponseKeys(data)

            return data

        except requests.exceptions.ConnectionError as e:
            self.logger.error('A connection error has occurred: %s.  Exiting.' % e)
            sys.exit(1)

    def printResponseKeys(self, data):
        """Prints a formatted list of keys to STDOUT"""
        merged_dicts = {}
        for item in data:
            merged_dicts.update(item)
        print('--------------------')
        print('Available Keys')
        print('--------------------')
        for key in [str(key) for key in merged_dicts]:
            print(key)
        print('--------------------')
        sys.exit(0)

    def writeDictToCsvFile(self, dictionary, filePath):
        """Writes JSON to a csv file with a header row"""
        with open(filePath, 'w') as csvfile:
            fieldnames = self.getColumnHeaders(dictionary)
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, dialect='excel', extrasaction='ignore')
            writer.writerow(dict(zip(fieldnames, fieldnames)))
            for row in dictionary:
                for item in row:
                    item = item.replace(",", "")
                writer.writerow(row)

    def getColumnHeaders(self, data):
        """Gets column headers from the passed data dictionary"""
        # Must iterate through and combine all keys into a single dictionary, to
        # ensure we don't miss any.
        merged_dicts = {}
        for item in data:
            merged_dicts.update(item)

        if len(self.keepFields) > 0:
            for key in list(merged_dicts):
                if key not in self.keepFields:
                    merged_dicts.pop(key, None)

        if len(self.discardFields) > 0:
            for item in self.discardFields:
                merged_dicts.pop(item, None)

        return [key for key in merged_dicts]

    def isJSON(self, string):
        """Tests if a string is a valid JSON"""
        try:
            json.loads(string)
        except ValueError:
            return False
        return True

    def isXML(self, string):
        """Tests if a string is a valid XML"""
        # Python 2.7 added the ParseError Exception.  For backwards compatability with 2.6,
        # we need to add the following if/else
        if hasattr(xml.etree.ElementTree, 'ParseError'):
            ETREE_EXCEPTIONS = (
                xml.etree.ElementTree.ParseError, xml.parsers.expat.ExpatError)
        else:
            ETREE_EXCEPTIONS = (xml.parsers.expat.ExpatError)
        try:
            ElementTree.fromstring(string)
        except ETREE_EXCEPTIONS:
            return False
        return True

    def setUrl(self, url):
        """Sets the instance URL"""
        self.url = url
        return self

    def setUsername(self, username):
        """Sets the instance username"""
        self.username = username
        return self

    def setPassword(self, password):
        """Sets the instance password"""
        self.password = password
        return self

    def addKeepFields(self, *columnHeaders):
        """Adds columns headers that are to be written to the CSV.  If this is set
        all other columns will be discarded"""
        self.keepFields.extend(columnHeaders)
        return self

    def addDiscardFields(self, *columnHeaders):
        """Adds columns headers that are to be written to the CSV.  If this is set
        all other columns will be discarded"""
        self.discardFields.extend(columnHeaders)
        return self

    def addNestingFields(self, *columnHeaders):
        """TODO Adds columns headers that are to be written to the CSV.  If this is set
        all other columns will be discarded"""
        self.nodesToTraverse.extend(columnHeaders)
        return self

    def areBothListsPopulated(self, list1, list2):
        """Returns true if there are both Keep and Discard fields defined """
        return len(list1) > 0 and len(list2) > 0

    def nodeTraversalGenerator(self, nodeList):
        """Traverses through each element in nodeList and yields the value"""
        for node in nodeList:
            yield node


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(
        description='''
            RequestToFile send an http request out expecting a JSON formatted
            response.  This response is transformed into a csv.  See sample.ini
            file for setting up the configuration
            '''
    )
    parser.add_argument(
        "config",
        help="the configuration file",
        metavar="config_file"
    )
    parser.add_argument(
        "output",
        help="the path of the output csv file",
        metavar="output_file_path"
    )
    parser.add_argument(
        "--headers",
        action='store_true',
        help="makes a request to the URL and prints the column headers to STDOUT",
    )
    if len(sys.argv) == 1:
        parser.print_help()
    args = parser.parse_args()

    logger.info("Beggining task.  Initialzing using file " + args.config)
    rtf = RequestToFile().initFromConfigFile(args.config)

    logger.info("Requesting data...")
    if args.headers:
        rtf.fetchDataFromURL(True)
    data = rtf.fetchDataFromURL()

    logger.info("Data recevied, writing to " + args.output)
    rtf.writeDictToCsvFile(data, args.output)

    logger.info("Task complete")
