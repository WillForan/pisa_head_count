#!/usr/bin/env python3
import soccerimg as si
import pandas as pd
import sys
import re
# https://docs.python.org/2/library/email-examples.html
from email.mime.text import MIMEText

# https://stackoverflow.com/questions/73781/sending-mail-via-sendmail-from-python
from subprocess import Popen, PIPE

def ascii_only(x):
    " remove weird non-ascii chars"
    x = re.sub(r'[^\x00-\x7F]','', x) 
    return(x)

config = si.read_config()
img_base = config['host']['imglink']
me = config['email']['from']

match_date = si.get_match_date()
dayrow = si.game_roster(match_date)
print("game")
print(dayrow)

try:
    next_game = si.game_roster(si.get_match_date(week_offset=1))
    next_str = "next game: %s %s"%(next_game.date.values[0], next_game.time.values[0])
    next_str = ascii_only(next_str) # remove weird non-ascii chars
except:
    print("failed to get next game")
    next_str="next game: TBD"

    

if dayrow is None:
    print("no dayrow for %s", match_date)
    sys.exit()

# e.g. 6/7 6v6 8:50
msg = """
<html>
<head></head>
<body>
<p> Who's in?</p>
<br><br>
%(msg)s
<br><br>
<ul>
  <li>
     <a href="%(gdoc)s">%(next_str)s (sheet)</a></li>
  <li>$%(cost)s via venmo
       <a href="https://venmo.com/%(venmo_id)s">@%(venmo_id)s</a>
       or <a href="http://paypal.me/%(paypal_id)s/%(cost)s">paypal</a> <br>
  </li>
</ul>

<a href="%(img)s">
<img src="%(img)s">
</a>
</body></html>
"""

urls = {'img': "%s?date=%s" % (img_base, match_date),
        'page': config['roster']['page'],
        'gdoc': config['roster']['doc'],
        'cost': config['pay']['cost'],
        'paypal_id': config['pay']['paypal_id'],
        'venmo_id': config['pay']['venmo_id'],
        'next_str': next_str,
        'msg': ""}


df = pd.read_csv(config['email']['tsv'], sep='\t')
hasemail = re.compile('@')
emails = [x for x in df.email.tolist() if hasemail.search(str(x))]
print(emails)
to = "; ".join(emails)
# from email.mime.multipart import MIMEMultipart
# mail = MIMEMultipart('alternative')
# mail.attach(MIMEText(msg, 'html'))
print("sending to")
print(to)

if(len(sys.argv) > 1):
    urls['msg'] = sys.argv[1]

subj_str = "[Sunday soccer] %(time)s (%(date)s) " % \
        {'date': ascii_only(match_date), 'time': ascii_only(dayrow['time'].values[0])}

mail = MIMEText(msg % urls, 'html')
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
