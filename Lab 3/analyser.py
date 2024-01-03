import csv
import sys
import re
from datetime import datetime

file_path = './extractor/kazimieras_mail.csv'
output_file_path = './processed_kazimieras_mail.csv'
output_header = [
    "Class","H_len","H_upp_len","H_dot","H_com","H_lt","CC_exists","S_len",
    "S_upp_len","S_emoji_has","S_lit_has","S_percent_has","S_dollar_has",
    "S_euro_has","S_excl_has","S_dot_has","S_bold_has","S_quote_count",
    "S_dot_count","S_dash_count","S_excl_count","Time_minutes_past","B_len",
    "B_upp_len","B_emoji_has","B_lit_has","B_percent_has","B_dollar_has",
    "B_euro_has","B_excl_has","B_dot_has","B_bold_has","B_quote_count",
    "B_dot_count","B_dash_count","B_excl_count","B_subscribe_has","B_https_has",
    "B_html_has","B_tag_len"]

all_rows = []
# Set the maximum field size to a higher limit (1gigabitas)
csv.field_size_limit(2**30)



def contains_emoji(s):
    # Emoji ranges as per Unicode standards
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    return int(emoji_pattern.search(s) is not None)

def contains_lithuanian_characters(s):
    lithuanian_pattern = re.compile(r'[ĄČĘĖĮŠŲŪŽąčęėįšųūž]')
    return int(bool(lithuanian_pattern.search(s)))

def time_from_even_hour(date_str):
    # Find the time part using regular expression
    match = re.search(r'(\d{2}:\d{2}:\d{2})', date_str)
    if not match:
        raise ValueError(f"No valid time found in string: {date_str}")

    # Extract the time part
    time_part = match.group(1)

    # Parse the time part
    time = datetime.strptime(time_part, '%H:%M:%S')

    # Calculate minutes from the even hour
    minutes = time.minute + time.second / 60
    if minutes > 30:
        minutes = 60 - minutes

    return round(minutes, 2)


##################################################################################

def calc_attributes(email):
    # attributes[0] = 1 jei emailas123456789
    attributes = []
    attributes.append( 0 )
    attributes.extend( attributes_from( email[0] ))
    attributes.extend( attributes_cc( email[2] ))
    attributes.extend( attributes_subject( email[3] ))
    attributes.extend( attributes_date( email[4] ))
    attributes.extend( attributes_body( email[5] ))

    return attributes

##################################################################################

def attributes_from(from_string):
    attributes = []
    attributes.append(len(from_string)) # header length
    attributes.append(round(sum(1 for char in from_string if char.isupper())/len(from_string),2)) # header uppercase-length ratio 
    attributes.append(int('<' in from_string and '.' in from_string.split('<')[0])) # header contains . before e-mail adress
    attributes.append(1 if ".com" in from_string else 0) # header contains ".com"
    attributes.append(1 if ".lt" in from_string else 0) # header contains ".lt"

    return attributes


def attributes_cc(cc_string):
    attributes = []
    attributes.append(1 if len(cc_string) > 0 else 0) # cc exists

    return attributes


def attributes_subject(subject_string):
    attributes = []
    attributes.append(len(subject_string))  # subject length
    attributes.append(round(sum(1 for char in subject_string if char.isupper())/len(subject_string))) # subject uppercase-length ratio 
    attributes.append(contains_emoji(subject_string)) # subject contains emoji
    attributes.append(contains_lithuanian_characters(subject_string)) # subject contains lithuanian charachters
    attributes.append(1 if '%' in subject_string else 0) # subject contains '%'
    attributes.append(1 if '$' in subject_string else 0) # subject contains '$'
    attributes.append(1 if '€' in subject_string else 0) # subject contains '€'
    attributes.append(1 if '!' in subject_string else 0) # subject contains '!'
    attributes.append(1 if '.' in subject_string else 0) # subject contains '.'
    attributes.append(int(bool(re.search(r'[\U0001D400-\U0001D7FF]', subject_string)))) # subject contains bold unicode characters
    attributes.append(subject_string.count('"')) # subject count of '"'
    attributes.append(subject_string.count('.')) # subject count of '.'
    attributes.append(subject_string.count('-')) # subject count of '-'
    attributes.append(subject_string.count('!')) # subject count of '!'

    return attributes


def attributes_date(date_string):
    attributes = []
    attributes.append(time_from_even_hour(date_string)) # time from closes hour (in minutes)
    return attributes


def attributes_body(body_string):
    attributes = []
    attributes.append(len(body_string)) # body length
    attributes.append(round(sum(1 for char in body_string if char.isupper())/len(body_string))) # body uppercase-length ratio 
    attributes.append(contains_emoji(body_string)) # body contains emoji
    attributes.append(contains_lithuanian_characters(body_string)) # body contains lithuanian charachters
    attributes.append(1 if '%' in body_string else 0) # body contains '%'
    attributes.append(1 if '$' in body_string else 0) # body contains '$'
    attributes.append(1 if '€' in body_string else 0) # body contains '€'
    attributes.append(1 if '!' in body_string else 0) # body contains '!'
    attributes.append(1 if '.' in body_string else 0) # body contains '.'
    attributes.append(int(bool(re.search(r'[\U0001D400-\U0001D7FF]', body_string)))) # body contains bold unicode characters
    attributes.append(round((body_string.count('"')*100)/len(body_string),2)) # body count of '"'
    attributes.append(round((body_string.count('.')*100)/len(body_string),2)) # body count of '.'
    attributes.append(round((body_string.count('-')*100)/len(body_string),2)) # body count of '-'
    attributes.append(round((body_string.count('!')*100)/len(body_string),2)) # body count of '!'
    attributes.append(1 if "subscribe" in body_string else 0) # body contains "subscribe"
    attributes.append(1 if "https://" in body_string else 0) # body contains "https://"
    attributes.append(1 if ("<html>" in body_string) or ("!DOCTYPE" in body_string) else 0) # body contains "<html>" or "!DOCTYPE"
    attributes.append(round((min(body_string.count('<'),body_string.count('>'))*100)/len(body_string),2)) # body '<>'-length ratio
    return attributes

##################################################################################

# Open the file and read it using csv.reader
with open(file_path, newline='',encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter='|')

    next(reader, None) 

    # Open the output file
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outputfile:
        
        writer = csv.writer(outputfile)
        writer.writerow(output_header)
        # Iterate through each row in the input CSV
        for row in reader:
            attributes = calc_attributes(row)
            writer.writerow(attributes)

print("Processing complete. Output saved to", output_file_path)


