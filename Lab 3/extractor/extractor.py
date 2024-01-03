import imaplib
import email
import csv
from email.header import decode_header
import re


# Function to decode and clean email strings
def clean_email_string(raw_email_string):
    if raw_email_string:
        decoded_parts = decode_header(raw_email_string)
        return ' '.join(
            part.decode(charset or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
            for part, charset in decoded_parts
        ).replace('\n', ' ').replace('\r', ' ')
    return ''

# Your login credentials
# email_address = "kazimieras.jasaitis@yahoo.com"
# app_password = "xxxxxxxxxxxxxxxx"  

# imap_server = imaplib.IMAP4_SSL("imap.mail.yahoo.com", 993)

# email_address = "kazimieras.jasaitis@gmail.com"
# app_password = "xxxx xxxx xxxx xxxx" 
# output_file_name = 'kazimieras_mail.csv'

email_address = "emailas123456789@gmail.com"
app_password = "xxxx xxxx xxxx xxxx" # Use app-specific password if 2FA is enabled
output_file_name = 'emailas_mail.csv'

imap_server = imaplib.IMAP4_SSL("imap.gmail.com", 993)



try:
    # Login to the server
    imap_server.login(email_address, app_password)

    # Select the mailbox (e.g., INBOX)
    imap_server.select('INBOX')

    # Search for all emails in the inbox
    status, email_ids = imap_server.search(None, 'ALL')
    if status != 'OK':
        print("No emails found!")
        exit()
    
    
    # Prepare CSV file for saving email data
    with open(output_file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|', quotechar='"', quoting=csv.QUOTE_ALL)

        # Write CSV Header
        writer.writerow(["From", "To", "Cc", "Subject", "Date", "Body"])
        email_n = 0
        # Fetch all email IDs
        email_id_list = email_ids[0].split()
        latest_email_ids = email_id_list[-600:] if len(email_id_list) > 600 else email_id_list

        for email_id in latest_email_ids:
            if email_n <500:
                try:
                    # Fetch the size of the email
                    status, size_data = imap_server.fetch(email_id, '(RFC822.SIZE)')
                    if status != 'OK':
                        print(f"Error fetching size of email {email_id}")
                        continue

                    # Parse the size data
                    try:
                        # Extract the size using regular expression
                        match = re.search(r'\d+', str(size_data[0]))
                        if match:
                            email_size = int(match.group())
                        else:
                            raise ValueError("Size not found in response")

                        # Skip emails larger than 1000 KB
                        if email_size > 1000 * 1024:
                            print(f"Skipping email {email_id} due to size ({email_size} bytes)")
                            continue
                    except ValueError as e:
                        print(f"Error parsing size for email {email_id}: {e}")
                        continue

                    status, data = imap_server.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        print(f"Error fetching email {email_id}")
                        continue

                    # Parse the email content
                    email_message = email.message_from_bytes(data[0][1])

                    # Extract email details
                    from_header = clean_email_string(email_message["From"])
                    to_header = clean_email_string(email_message["To"])
                    cc_header = clean_email_string(email_message.get("Cc", ""))
                    subject = clean_email_string(email_message["Subject"])
                    date = email_message["Date"]

                    # Process email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Ignore attachment parts
                            if "attachment" not in content_disposition and part.get_payload(decode=True) is not None:
                                try:
                                    body_part = part.get_payload(decode=True)
                                    charset = part.get_content_charset() or 'utf-8'
                                    body += body_part.decode(charset, errors='ignore').replace('\n', ' ').replace('\r', ' ')
                                except Exception as e:
                                    print(f"Error processing part of email {email_id}: {e}")
                                    continue
                    else:
                        try:
                            body = email_message.get_payload(decode=True)
                            if body is not None:
                                charset = email_message.get_content_charset() or 'utf-8'
                                body = body.decode(charset, errors='ignore')
                            else:
                                body = ''
                            body = body.replace('\n', ' ').replace('\r', ' ')
                        except Exception as e:
                            print(f"Error processing email {email_id}: {e}")
                            continue

                    # Write to CSV
                    writer.writerow([from_header, to_header, cc_header, subject, date, body])
                    email_n += 1
                    print(f"email #{email_n} processed successfully.")
                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue  # Skip to the next email
            else:
                break

    print(f"Emails have been saved to {output_file_name} (delimiter - '|')")

    # Close the mailbox
    imap_server.close()

except Exception as e:
    print("An error occurred:", e)

finally:
    # Logout from the server
    imap_server.logout()
