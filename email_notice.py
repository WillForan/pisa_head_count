#!/usr/bin/env python3
import soccerimg as si
import pandas as pd
import sys
import os
import re
# https://docs.python.org/2/library/email-examples.html
from email.mime.text import MIMEText

# https://stackoverflow.com/questions/73781/sending-mail-via-sendmail-from-python
from subprocess import Popen, PIPE


def ascii_only(x):
    " remove weird non-ascii chars"
    x = re.sub(r'[^\x00-\x7F]', '', x)
    return(x)


if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print("Provide config file to use as first argument!")
    sys.exit(1)

# read in config file
config = si.read_config(sys.argv[1])
img_base = config['host']['imglink']
me = config['email']['from']
email_header = config['email']['header']
email_url = config['email']['tsv']
dow = int(config['roster']['dow'])  # 2=wednesday, 6=sunday
email_fill = {'page': config['roster']['page'],
              'gdoc': config['roster']['doc'],
              'cost': config['pay']['cost'],
              'paypal_id': config['pay']['paypal_id'],
              'venmo_id': config['pay']['venmo_id'],
              'next_str': '',
              'img': "",
              'msg': ""}

match_date = si.get_match_date(dow)
print(match_date)
dayrow = si.game_roster(match_date, config_file=sys.argv[1])
print("game")
print(dayrow)

try:
    next_game = si.game_roster(si.get_match_date(dow, week_offset=1),
                               config_file=sys.argv[1])
    next_str = "next game: %s %s" % \
               (next_game.date.values[0], next_game.time.values[0])
    next_str = ascii_only(next_str)  # remove weird non-ascii chars
except Exception:
    print("failed to get next game")
    next_str = "next game: TBD"


if dayrow is None:
    print("no dayrow for %s", match_date)
    sys.exit()

# read in message tempalte from file
with open("standard_message.html", 'r') as f:
    msg = f.read()

email_fill['next_str'] = next_str
email_fill['img'] = "%s?date=%s&config=%s" % \
                    (img_base, match_date, os.path.basename(sys.argv[1], ".ini"))

if config['roster']['page']:
    email_fill['page'] = """
    <li>
       <a href="%s">league page</a>
    </li>
    """ % config['roster']['page']
else:
    email_fill['page'] = ""

df = pd.read_csv(email_url, sep='\t')
hasemail = re.compile('@')
emails = [x for x in df.email.tolist() if hasemail.search(str(x))]
print(emails)
to = "; ".join(emails)
# from email.mime.multipart import MIMEMultipart
# mail = MIMEMultipart('alternative')
# mail.attach(MIMEText(msg, 'html'))
print("sending to")
print(to)

if(len(sys.argv) > 2):
    email_fill['msg'] = " ".join(sys.argv[2:])

subj_str = "%(header)s %(time)s (%(date)s) %(field)s" % \
        {'header': email_header,
         'field': ascii_only(dayrow['field'].values[0]),
         'date': ascii_only(match_date),
         'time': ascii_only(dayrow['time'].values[0])}

mail = MIMEText(msg % email_fill, 'html')
mail['Subject'] = subj_str
mail['To'] = to
mail['From'] = me

print(mail)
print("\n\n")
if input('** Send? (y/N): ') != 'y':
    print('quiting')
    sys.exit()

# use local sendmail to send
p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
p.communicate(mail.as_bytes())
