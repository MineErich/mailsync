import imaplib
import email
from email.header import decode_header
import os
import json
import logging
import sys

def load_synced_uids(mailbox):
    """Lädt die UIDs bereits synchronisierter E-Mails für eine Mailbox."""
    if mailbox in LAST_UID:
        return LAST_UID[mailbox]
    else:
        return 0

def save_synced_uid(mailbox, uid):
    """Speichert eine neue UID, nachdem eine E-Mail erfolgreich heruntergeladen wurde."""
    with open(CONFFILE, 'r+') as f:
        data = json.load(f)
        data['last_uid'].update({mailbox: uid})
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def connect_to_mailbox(mailbox):
    """Verbindet sich mit einem Mailbox-Ordner."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    # mail.select(mailbox, readonly=True)

    status, _ = mail.select(mailbox, readonly=True)
    if status != "OK":
        logging.error(f"Fehler beim Öffnen der Mailbox: {mailbox}")
        mail.logout()
        return None  # Fehlerbehandlung

    return mail

def save_attachment(part, output_dir, uid):
    """Speichert einen E-Mail-Anhang."""
    filename = part.get_filename()
    if filename:
        filepath = os.path.join(output_dir, f"{uid}_{filename}")
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        logging.debug(f"Anhang gespeichert: {filepath}")

def save_email(msg, uid, output_dir):
    try:
        """Speichert die E-Mail und ihre Anhänge."""
        # Betreff verarbeiten
        if msg["Subject"] is None:
            subject = "no_subject"  # Standardwert für E-Mails ohne Betreff
        else:
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
        safe_subject = "".join(c for c in subject if c.isalnum() or c in " _-").strip()
        filename = f"{uid}_{safe_subject or 'no_subject'}.eml"

        # E-Mail speichern
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(msg.as_bytes())
        logging.debug(f"E-Mail gespeichert: {filepath}")

        # Anhänge speichern
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") and "attachment" in part.get("Content-Disposition"):
                save_attachment(part, output_dir, uid)
    except:
        logging.error(f"E-Mail konnte nicht verarbeitet werden: {uid}")

def fetch_emails(mailbox):
    """E-Mails aus einem Postfach abrufen und speichern."""
    # Lokalen Speicherordner sicherstellen
    mailbox_folder = os.path.join(LOCAL_FOLDER, mailbox.replace("/", "_"))
    os.makedirs(mailbox_folder, exist_ok=True)

    mail = connect_to_mailbox(mailbox)

    if mail is None:
        logging.warning(f"Überspringe {mailbox} wegen Verbindungsfehler.")
        return

    # Alle E-Mail-UIDs abrufen
    status, messages = mail.search(None, "ALL")
    if status != "OK":
        logging.error(f"Fehler beim Abrufen von E-Mails aus {mailbox}")
        mail.close()
        mail.logout()
        return

    uids = messages[0].split()    
    for uid in uids:
        uid_str = uid.decode()
        if int(uid_str) <= load_synced_uids(mailbox):
            continue  # Überspringe bereits gespeicherte E-Mail

        status, msg_data = mail.fetch(uid, "(RFC822)")
        if status != "OK":
            logging.error(f"Fehler beim Abrufen von UID {uid.decode()}")
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                save_email(msg, uid_str, mailbox_folder)

    if len(uids) == 0:
        latest_uid = 0
    else:
        latest_uid = uids[-1]
        latest_uid= int(latest_uid.decode())
    save_synced_uid(mailbox, latest_uid)

    mail.close()
    mail.logout()


def init_sync(conf):
    # Konfiguration
    global CONFFILE, IMAP_SERVER, IMAP_USER, IMAP_PASSWORD, MAILBOXES, LOCAL_FOLDER, LAST_UID, LOGFILE
    CONFFILE = conf
    with open(CONFFILE) as config_file:
        config = json.load(config_file)

    IMAP_SERVER = config["imap_server"]
    IMAP_USER = config["imap_user"]
    IMAP_PASSWORD = config["imap_password"]
    MAILBOXES = config["mailboxes"]
    LOCAL_FOLDER = config["local_folder"]
    LAST_UID = config["last_uid"]
    LOGFILE = config["logfile"]

    # logging
    FORMAT = '%(asctime)s %(levelname)s [%(funcName)s] %(message)s'
    logging.basicConfig(filename=LOGFILE, encoding='utf-8', level=logging.INFO, format=FORMAT)

    # log name of conffile
    logging.debug(f"using {CONFFILE}")

    # start syncing
    for mailbox in MAILBOXES:
        logging.debug(f"Synchronisiere Ordner: {mailbox}")
        fetch_emails(mailbox)

if __name__ == "__main__":
    # Konfiguration
    if len(sys.argv) == 2:
        CONFFILE = sys.argv[1]
    else:
        CONFFILE = "config.json"
    init_sync(CONFFILE)
