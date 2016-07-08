import json
import logging
from optparse import OptionParser
import subprocess
from sqlite3 import *
import thread
import time

# Hipchat creds and my user id
hipchat_url = "https://hipchat.company.com"
hipchat_auth_token = ""
hipchat_user_id = 1

name = "ben"

parser = OptionParser()
parser.add_option("-d", "--dbname", dest="dbname", default="say_what",
                  help="name of the sqlite3 database", metavar="DBNAME")
parser.add_option("-l", "--logpath", dest="logpath", default="/var/log/say_my_name.log",
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


def recent_mention(search_string):
    query = '''
    SELECT
        created_time, minutes
    FROM
        recordings
    WHERE
        created_time > ? and minutes ilike '%?%
    ORDER BY
        created_time DESC
    LIMIT 1'
    '''
    seconds = time.time() - 60 # Look 1 minute back. 
    date = datetime.datetime.fromtimestamp(int(seconds))
    try:
        cur.execute(query, (date.strftime('%Y-%m-%d %H:%M:%S') , search_string))
    except Exception as exc:
        logging.error('Failed to query for {}'.format(search_string))
    return cur.fetchone()


def notify(user_id, auth_token, message):
    # Send the conversation context to yourself on hipchat
    data = {
        'message': message,
        'notify': True,
        'message_format': 'text'
    }

    r = requests.post('{}/v2/user/{}/message'.format(hipchat_url, user_id),
        data=json.dumps(data),
        headers = {
            'content-type': 'application/json',
            "Authorization": "Bearer {}".format(auth_token)
            }
        )


def muted():
    # Play the "Sorry, I was on mute" audio file.
    audio_file = "./Muted.m4a"
    # This works on my macbook,
    # change the command line tool to another one if on a different OS
    audio_output = subprocess.call(["afplay", audio_file])


while True:
    mentioned = recent_mention(name)
    if not mentioned:
        # It doesn't make sense to sleep for 1 second, and then search for a minute back.
        # So instead we will sleep for 5 seconds, and then just to make sure that Watson
        # had time to translate the voice recording, search 1 minute back.
        time.sleep(5)
        continue
    mention_time = mentioned[0]
    logging.info("You were mentioned!")
    minutes = mentioned[1]
    try:
        thread.start_new_thread(notify, (hipchat_user_id, hipchat_auth_token, minutes))
    except Exception as exc:
        logging.error('Failed to start new thread\n{}'.format(exc))

    while int(time.time() - mention_time) < 15:
        time.sleep(1)

    muted()
    # Wait another minute before checking for name mentions
    time.sleep(60)
