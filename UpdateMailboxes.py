import imaplib
import json
import sys
import logging

def save_synced_uid(folder_names, conf):
    """Speichert eine neue UID, nachdem eine E-Mail erfolgreich heruntergeladen wurde."""
    with open(conf, 'r+') as f:
        data = json.load(f)
        data.update({"mailboxes": folder_names})
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def update_mailboxes(conf):
    try:
        # logging
        FORMAT = '%(asctime)s %(levelname)s [%(funcName)s] %(message)s'
        logging.basicConfig(filename='UpdateMailBoxes.log', encoding='utf-8', level=logging.INFO, format=FORMAT)

        logging.debug(f"using {conf}")

        with open(conf) as config_file:
            config = json.load(config_file)
        IMAP_SERVER = config["imap_server"]
        IMAP_USER = config["imap_user"]
        IMAP_PASSWORD = config["imap_password"]

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        status, mailboxes = mail.list()
        folder_names = []
        for mailbox in mailboxes:
            m = mailbox.decode()
            m_name = m.split(' \".\" ')[-1]
            m_name = m_name.replace("\"","")
            folder_names.append(m_name)

        for i in range(0, len(folder_names)):
            if " " in folder_names[i]:
                folder_names[i] = '\"'+folder_names[i]+'\"'

        save_synced_uid(folder_names, conf)
        logging.debug(f"updated list of mailboxes in {conf}")
    
    except:
        logging.error(f"Konnte Mailboxen nicht aktualisieren für: {conf}")


if __name__ == "__main__":
    # Konfiguration
    if len(sys.argv) == 2:
        CONFFILE = sys.argv[1]
    else:
        CONFFILE = "config.json"
    update_mailboxes(CONFFILE)