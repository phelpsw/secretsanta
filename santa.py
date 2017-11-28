import random
import smtplib
import argparse
import json
import logging
from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def pick_non_matching(santa, remaining):

    if len(remaining) == 0:
        return None
    if len(remaining) == 1:
        if remaining[0] == santa:
            return None

    while True:
        target = random.choice(remaining)
        if target != santa:
            return target

def assign(santas):
    complete = False
    while not complete:
        remaining = list(santas)
        matches = []
        for santa in santas:
            target = pick_non_matching(santa, remaining)
            if not target:
                # Deadlock has been reached, break out of this attempt
                break

            matches.append((santa, target))
            remaining.remove(target)
            if len(remaining) == 0:
                complete = True
    return matches

parser = argparse.ArgumentParser(description='Pick secret santas and send email')
parser.add_argument('server', type=str, help='SMTP server')
parser.add_argument('port', type=int, help='SMTP port')
parser.add_argument('user', type=str, help='Username')
parser.add_argument('password', type=str, help='Password')
parser.add_argument('config', type=str, help='Config file')
parser.add_argument('--debug', action='store_true', help='Dont send email and print')
args = parser.parse_args()

with open(args.config, 'r') as f:
    logger = logging.getLogger('secretsanta')
    hdlr = logging.FileHandler('assignment-{}.log'\
                               .format(datetime.now().isoformat()))
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    cfg = json.load(f)
    santas = cfg['santas']
    from_addr = cfg['from']

    matches = assign(santas)

    server = smtplib.SMTP_SSL(args.server, args.port)
    server.login(args.user, args.password)

    for match in matches:
        body = 'Hi {}, you are the secret santa for {}.'\
                .format(match[0][0], match[1][0])

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = match[0][1]
        msg['Subject'] = "Secret Santa Assignment"
        msg.attach(MIMEText(body, 'plain'))
        logger.info(body)
        if args.debug:
            print(body)
        else:
            server.sendmail(from_addr, match[0][1], msg.as_string())

