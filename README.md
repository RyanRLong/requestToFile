# requestToFile

![Travis](https://travis-ci.org/SaltyCatFish/requestToFile.svg)
[![GitHub release](https://img.shields.io/github/release/qubyte/rubidium.svg?maxAge=2592000)]()
[![Twitter URL](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&maxAge=2592000)](https://twitter.com/SaltyCatFish)

requestToFile is a command line driven Python module that makes an http request with authorization to a url using a configuration file and formats the response into a csv file.  

The module functions by making an http request using the `requests` package.  Once the response is received, requestToFile checks its return transport type, converting it from XML to JSON if the response is not already in JSON format.  Based on the configuration file (see below), requestToFile will traverse the JSON until it finds its final node destination.  The application will then grab all of the nodes and compile a list of headers comprising all available headers of all available entries.

requestToFile will then keep or discard fields based on the configuration file (see below).  *It is important to keep in mind that `[KEEP_FIELDS]` and `[DISCARD_FIELDS]` are mutually exclusive, and having entries in both will throw an error*.

Lastly, request to file will take the remaining information and write it to a csv file.

requestToFile supports Python 2.6 or greater and Python 3.2 or greater.

## Requirements
* [Python](https://www.python.org/downloads/ "Python Download Page") 2.6 or 3.2 and greater 
* requests==2.10.0
* xmltodict==0.10.1

## Installation and Setup
To install requestToFile, clone this repository to your local machine by typing the following at the command line:
```bash
git clone https://github.com/SaltyCatFish/requestToFile.git
```
Once the source is downloaded, you will need to install the dependencies listed in the requirements.txt file.  Provided you have PIP installed, you can use the following command to download dependencies:
```bash
pip install -r requirements.txt
```
## Running
requestToFile operates by making an http request based off parameters used in a config file.  The typical usage is:
```bash
python requestToFile <config_file> <output_file>
```
The configuration file is explained below.  The output_file is the destination your csv file will be written to.

To see command line help type:
```
python requestToFile.py
```

There is a `--headers` flag that will make the request, but will only print out the available column headers based on the configuration file and the response returned.  This is useful for fine tuning configuration files and error checking.

### Configuration File


#### [NESTING]
fields = an array of nodes to traverse when gathering the data you need.  For example, say you have an XML response like so:

![xml-example](http://blog.sqlauthority.com/i/b/samplexml.jpg)

If you only wanted the values of the `<Fruits>` subtree, you would setup the `[NESTING]` in your configuration file like so:

```bash
[NESTING]  
fields = ["SampleXML", "Fruits"]
```



## Log

**v0.0.2** - add full support for Python 3







