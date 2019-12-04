This tool takes a configuration file containing the names and email addresses
of participants and randomly assigns another person as their secret santa.
The tool emails each of the participants the name of the person they are secret
santa for.

Creates a log of assignments if required.

Updated for python 3.6+

## General Usage
```
python santa.py <smtpserver> <smtpport> <username> <password> config.json
```

## Fastmail
```
python santa.py mail.messagingengine.com 465 <username> <password> config.json
```

## Review Log
```
cat assignment-2019-12-04T09\:51\:00.941409.log | grep "Hi User 1"
```
