import json
import logging
import sys

import mailsync as mailsync
import UpdateMailboxes as upMB

# Konfiguration
if len(sys.argv) == 2:
    CONFFILE = sys.argv[1]
else:
    CONFFILE = "deamon.json"
with open(CONFFILE) as config_file:
    config = json.load(config_file)

LOGFILE = config["logfile"]

# logging
FORMAT = '%(asctime)s %(levelname)s [%(funcName)s] %(message)s'
logging.basicConfig(filename=LOGFILE, encoding='utf-8', level=logging.INFO, format=FORMAT)

# log name of conffile
logging.debug(f"using {CONFFILE}")


for mailaccount in config["mailaccounts"]:
    logging.info(f"updating {mailaccount}")
    print(f"updating {mailaccount}")
    upMB.update_mailboxes(mailaccount)

    logging.info(f"syncing {mailaccount}")
    print(f"syncing {mailaccount}")
    mailsync.init_sync(mailaccount)
