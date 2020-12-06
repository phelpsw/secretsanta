import random
import smtplib
import argparse
import json
import logging
from datetime import datetime
from email.message import EmailMessage

def pick_non_matching(santa, remaining, history):
    filt_history = list(filter(lambda x: x['santa']['name'] == santa['name'], history))
    remaining = list(filter(lambda x: x['name'] not in [y['recipient']['name'] for y in filt_history], remaining))

    if len(remaining) == 0:
        return None
    if len(remaining) == 1:
        if remaining[0] == santa:
            return None

    while True:
        target = random.choice(remaining)
        if target != santa:
            return target

def assign(santas, history):
    attempts = 0
    complete = False
    while not complete:
        remaining = list(santas)
        matches = []
        for santa in santas:
            attempts += 1
            if attempts > 100:
                raise Exception("Unsolvable")

            target = pick_non_matching(santa, remaining, history)
            if not target:
                # Deadlock has been reached, break out of this attempt
                break

            matches.append({"santa": santa, "recipient": target})
            remaining.remove(target)
            if len(remaining) == 0:
                complete = True
    return matches

parser = argparse.ArgumentParser(description='Pick secret santas and send email')
parser.add_argument('server', type=str, help='SMTP server')
parser.add_argument('port', type=int, help='SMTP port')
parser.add_argument('user', type=str, help='Username')
parser.add_argument('password', type=str, help='Password')
parser.add_argument('fromaddr', type=str, help='From Email Address')
parser.add_argument('config', type=str, help='Config file')
parser.add_argument('--history_input', type=str, help='History Input file')
parser.add_argument('--history_output', type=str, help='History Output file')
parser.add_argument('--debug', action='store_true', help='Dont send email and print')
args = parser.parse_args()

with open(args.config, 'r') as f:
    logger = logging.getLogger('secretsanta')
    hdlr = logging.FileHandler('assignment-{}.log'\
                               .format(datetime.now().isoformat()))
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    santas = json.load(f)
    from_addr = args.fromaddr

    history = []
    if args.history_input:
        with open(args.history_input, 'r') as history_f:
            history = json.load(history_f)

    matches = assign(santas, history)

    if args.history_output:
        with open(args.history_output, 'w') as history_out:
            json.dump(matches, history_out)

    if not args.debug:
        server = smtplib.SMTP_SSL(args.server, args.port)
        server.login(args.user, args.password)

    for match in matches:
        body = f"Hi {match['santa']['name']}, you are the secret santa for {match['recipient']['name']}."

        msg = EmailMessage()
        msg['From'] = from_addr
        msg['To'] = match['santa']['email']
        msg['Subject'] = "Secret Santa Assignment"
        msg.set_content(body)
        logger.info(body)
        if args.debug:
            print(body)
        else:
            server.sendmail(from_addr, match['santa']['email'], msg.as_string())

