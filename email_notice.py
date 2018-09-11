#!/usr/bin/env python3
import soccerimg as si
import pandas as pd
import sys
import re
# https://docs.python.org/2/library/email-examples.html
from email.mime.text import MIMEText

# https://stackoverflow.com/questions/73781/sending-mail-via-sendmail-from-python
from subprocess import Popen, PIPE

config = si.read_config()
img_base = config['host']['imglink']
me = config['email']['from']

match_date = si.get_match_date()
dayrow = si.game_roster(match_date)
print("game")
print(dayrow)

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
<p>
<a href="%(pisa)s"> PISA </a> | <a href="%(gdoc)s">sheet</a> <br><br>
</p>
<a href=%(gdoc)s>
<img src="%(img)s">
</a>
</body></html>
"""

urls = {'img': "%s?date=%s" % (img_base, match_date),
        'pisa': config['roster']['page'],
        'gdoc': config['roster']['doc'],
        'msg': ""}


df = pd.read_csv(config['email']['tsv'], sep='\t')
hasemail = re.compile('@')
emails = [ x for x in df.email.tolist() if hasemail.search(str(x))]
print(emails)
to = "; ".join(emails)
# from email.mime.multipart import MIMEMultipart
# mail = MIMEMultipart('alternative')
# mail.attach(MIMEText(msg, 'html'))
print("sending to")
print(to)

if(len(sys.argv) > 1):
    urls['msg'] = sys.argv[1]


mail = MIMEText(msg % urls, 'html')
mail['Subject'] = "[Thu PSL] %(time)spm (%(date)s) " % \
        {'date': match_date, 'time': dayrow['time'].values[0]}
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
