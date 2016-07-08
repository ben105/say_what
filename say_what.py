import json
import logging
from optparse import OptionParser
import requests
import speech_recognition as sr
import subprocess
from sqlite3 import *
import sys
import thread
import time

parser = OptionParser()
parser.add_option("-d", "--dbname", dest="dbname", default="say_what",
                  help="name of the sqlite3 database", metavar="DBNAME")
parser.add_option("-u", "--user", dest="ibm_user",
                  help="IBM speech to text user name", metavar="IBM_USERNAME")
parser.add_option("-p", "--password", dest="ibm_pass",
                  help="IBM speech to text password", metavar="IBM PASSWORD")
parser.add_option("-l", "--logpath", dest="logpath", default="/var/log/say_what.log",
                  help="filepath to the log file", metavar="LOGPATH")
parser.add_option("-q", "--loglevel", dest="loglevel", default="warning",
                  help="level of logging", metavar="LOGLEVEL")
options, args = parser.parse_args()

def get_level(level):
  if not level:
    return None
  lowercase_level = level.lower()
  if lowercase_level == "info":
      return logging.info
  if lowercase_level == "warning":
      return logging.warning
  if lowercase_level == "error":
      return logging.error
  if lowercase_level == "critical":
      return logging.critical
  if lowercase_level == "exception":
      return logging.exception
  if lowercase_level == "log":
      return logging.log

# Set up the connection to the database.
conn = sqlite3.connect(options.dbname)
cur = conn.cursor()

# Set up the logging.
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, filename=options.logpath, level=get_level(options.loglevel))

# IBM Speech to Text creds
IBM_USERNAME = ""
IBM_PASSWORD = ""

def translate(audio, r):
    results = None
    try:
        results = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
    except sr.UnknownValueError:
        # print("IBM Speech to Text could not understand audio")
        pass
    except sr.RequestError as e:
        print("Could not request results from IBM Speech to Text service; {0}".format(e))
    print("Results: {}".format(results))
    return results


def verify_sqltable_exists():
    query = '''
    SELECT name 
    FROM sqlite_master 
    WHERE type = 'table' AND name = 'recordings';
    '''
    try:
        cur.execute(query)
    except Exception as exc:
        print('Failed trying to find table\n{}'.format(exc))
        sys.exit(1)
    rows = cur.fetchall()
    if len(rows) == 0:
       cur.execute('CREATE TABLE recordings (created_time datetime, varchar(900));')

def write_to_db(results):
    try:
        cur.execute("INSERT INTO minutes VALUES (?, ?)",
                (time.time(), results))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print('Failed to write new data, "{}", into database {}\n{}'.format(results, options.dbname, exc))
        sys.exit(1)

def consumer(audio,r):
    # Received audio, now transcribe it and log it
    results = translate(audio,r)
    if results:
        write_to_db(results)
    else:
        print "[--Silence--]"


def main():
    if options.ibm_user is None or options.ibm_pass is None:
        parser.print_usage()
    verify_sqltable_exists()
    # Spawn index/notify/play-wav script subprocess
    subprocess.Popen(['python','./say_my_name.py', '-q', options.loglevel, '-d', options.dbname])
    r = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
            thread.start_new_thread(consumer, (audio,r))

if __name__ == '__main__':
    main()
