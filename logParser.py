#!/usr/bin/env python

__doc__="\
\n\nThis script takes apache log file as an argument and then generates a report\
\n\
\nSyntax : parser.py -o <absolute or relative path of file>\
\n\
\nExample parser.py -o sample.log \
\n\
"

__VER__=1.0

import sys
import datetime
import json
import logging
import optparse

logger = logging.basicConfig(level=logging.INFO)

initial_date = ""
prev_date = ""
count_lines = -1
count_get = 0
count_post = 0
agentDict = {}

'''
    This method collects the metrics for each user agent using dict
'''
def collect_agent_info(user_agent):
    global agentDict
    if agentDict.has_key(user_agent):
        agentDict[user_agent] = agentDict[user_agent]+1
    else:
        agentDict[user_agent]=0

def apache_output(line):
    global initial_date, count_lines, prev_date
    global count_get, count_post

    if line is None:
        logging.info("No of request served on %s = %d \n", prev_date, count_lines)
        logging.debug("Date Changed = %d", count_lines)
        logging.info("Ratio of request %d / %d on date %s \n", count_get, count_post, prev_date)
        return

    split_line = line.split()
    # Array item 3 has info about access date

    user_agent_info = split_line[11].split(':')[0].split("(")[0].replace("\"", "")
    logging.debug("User agent : %s", user_agent_info)
    collect_agent_info(user_agent_info)

    requestType=split_line[5].replace("\"","")
    if requestType == "POST":
        count_post+=1;
    elif requestType == "GET":
        count_get+=1;

    try:
        date_col = split_line[3].split(':')[0].replace("[", "")
        logging.debug("Date Value = %s", date_col)
        datetime.datetime.strptime(date_col, "%d/%b/%Y")
        if initial_date == "":
            count_lines=1;
            initial_date = split_line[3].split(':')[0]
        elif initial_date == split_line[3].split(':')[0]:
            logging.debug("Date Same = %d", count_lines)
            count_lines+=1;
            prev_date = date_col;
        else:
            logging.debug("Date Changed = %d", count_lines)
            logging.info("No of request served on %s = %d \n", prev_date, count_lines)
            logging.info("Ratio of request %d / %d on date %s \n", count_get, count_post, prev_date)
            count_lines=-1;
            count_get = 0;
            count_post = 0;
            initial_date = split_line[3].split(':')[0]
    except ValueError as err:
        logging.debug("Invalid Date format caught : %s \n",date_col)
        logging.debug(err)

def final_report(logfile):
    for line in logfile:
        line_dict = apache_output(line)
        logging.debug(line_dict)
    apache_output(None)
    logging.debug(json.dumps(agentDict,indent=4))
    sorted_dict = sorted(agentDict, key=agentDict.get, reverse=True)[:3]
    for value in sorted_dict:
        logging.info(" Top Accessor user agent {} with hits = {}".format(value, agentDict[value]))

if __name__ == "__main__":
    logging.debug('ARGV      :%s', sys.argv[1:])

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('-o', '--output',
                      dest="output_filename",
                      default="sample.out",
                      )
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      )
    parser.add_option('--version',
                      dest="version",
                      default=False,
                      action='store_true'
                      )

    options, remainder = parser.parse_args()

    if options.version:
        logging.info("App Version = {}".format(__VER__))
        sys.exit(0)

    if options.output_filename :
        try:
            infile = open(options.output_filename, 'r')
            if options.verbose:
                print("IS TRUE!")
                logger = logging.getLogger()
                logger.setLevel(level=logging.DEBUG)
                logger.debug("Is True")

            log_report = final_report(infile)
            infile.close()
        except IOError:
            logging.error("You must specify a valid file to parse")
            logging.info(__doc__)
            sys.exit(1)

    logging.debug('VERSION   : %s', options.version)
    logging.debug('VERBOSE   : %s', options.verbose)
    logging.debug('OUTPUT    : %s', options.output_filename)
    logging.debug('REMAINING : %s', remainder)
    sys.exit(0)


