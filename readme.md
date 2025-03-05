# MAILSYNC

Download all your mails from the mailserver and archive them (e.g. to Nextcloud), so you can make space for more mails on the mailserver.

This script will attempt to download all mails as .eml files and also all attachments.

Supports multiple mailaccounts and mailboxes.

# Installation

Download this repo duhh ;)

# Configuration

First create a config-file for the mailbox you want to sync
    {
      "imap_server": "imap.domain.de",  # insert the address to the imap server here
      "imap_user": "info@domain.de",    # insert username or mail address
      "imap_password": "password",      # insert password (ba warned: this is a plain text file)
      "local_folder": "emails/folder1",        # the downloaded files will be saved to this location
      "logfile": "mail2nc.log",         # path to and name of logfle (only used if script is called without deamon)
      "mailboxes": [],                  # this will be overwritten by the UpdateMailboxes-Script, so you won't need to enter anything
      "last_uid": {}                    # this will be overwritten by the mailsync-Script, so you won't need to enter anything
    }

Create a deamon.json

    {
        "logfile": "deamon.log",              # path to and name of logfle for deamon
        "mailaccounts": ["mailaccount.json"]  # list of all config-files (1 per mailaccount) that should be included for syncing
    }

# Use MAILSYNC

Call deamon.py either with a config-json-file, or just deamon.py, if the deamon config file is named deamon.json and is in the same dir as the .py

    # Case 1:
    python3 deamon.py path/to/deamon-config.json
    # Case 2:
    python3 deamon.py

# Syncing to another server

You could use rsync or WebDAV for syncing or do nothing.

# Syncing to Nextcloud

Use WebDAV to sync the mails to your Nextcloud. The Nextcloud Plugin "eml viewer" can show .eml files in Nextcloud, so consider installing it!

# cronjob

To automatically run the deamon use a cron job, e.g.

    crontab -e
    # add:
    */15 * * * * cd /path/to/mailsync && python3 deamon.py
