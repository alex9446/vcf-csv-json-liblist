import csv
import json
import re
import quopri
from sys import argv
from typing import Dict, List

Contact = Dict[str, str]
ContactList = List[Contact]


OPTIONS_DESC = '''
conversion:
--vcf2csv\t\t From VCard to CSV
--vcf2json\t\t From VCard to JSON
--csv2vcf\t\t From CSV to VCard
--csv2json\t\t From CSV to JSON
--json2vcf\t\t From JSON to VCard
--json2csv\t\t From JSON to CSV

--decode\t\t Decode quoted printable strings
--reducer\t\t Reduce phone attributes if they have the same value


WARNING: The conversion does not keep the value of duplicate attributes
'''
USAGE = ('usage: python3 {} <conversion> [--decode] [--reducer] <filename>\n{}'
         .format(argv[0], OPTIONS_DESC))
VERSION = '0.2.0'

QUOTED_PRINTABLE_ATTR = ';CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE'
PHONE_ATTR = [  # First value is the default
    'TEL;CELL;PREF',
    'TEL;CELL',
    'TEL;WORK'
]


def headers_of_contacts(list_of_contacts: ContactList) -> List[str]:
    headers = []

    for dict_of_contact in list_of_contacts:
        for key in dict_of_contact.keys():
            if key not in headers:
                headers.append(key)

    return headers


def decode_quoted_printable(list_of_contacts: ContactList) -> ContactList:
    new_list_of_contacts = []

    for dict_of_contact in list_of_contacts:
        new_dict_of_contact = {}
        for key, value in dict_of_contact.items():
            if key.endswith(QUOTED_PRINTABLE_ATTR):
                new_key = key.replace(QUOTED_PRINTABLE_ATTR, '')
                new_value = quopri.decodestring(value).decode('utf-8')
                new_dict_of_contact[new_key] = new_value
            else:
                new_dict_of_contact[key] = value
        new_list_of_contacts.append(new_dict_of_contact)

    return new_list_of_contacts


def reduce_phone_attr(list_of_contacts: ContactList) -> ContactList:
    default_phone_attr = PHONE_ATTR[0]
    new_list_of_contacts = []

    for dict_of_contact in list_of_contacts:
        new_dict_of_contact = {}
        for key, value in dict_of_contact.items():
            if (key in PHONE_ATTR[1:]
                and (default_phone_attr not in dict_of_contact
                     or dict_of_contact[default_phone_attr] == value)):
                new_dict_of_contact[default_phone_attr] = value
            else:
                new_dict_of_contact[key] = value
        new_list_of_contacts.append(new_dict_of_contact)

    return new_list_of_contacts


def vcf2list(filename: str, replace_same_key: bool = False) -> ContactList:
    raw_contacts = []
    list_of_contacts = []

    with open(filename) as f:
        raw_contacts = re.findall(r"BEGIN:VCARD(.*?)END:VCARD", f.read(), re.S)

    for raw_contact in raw_contacts:
        dict_of_contact = {}
        for contact_line in str(raw_contact).split('\n'):
            if contact_line:
                key, value = contact_line.split(':', maxsplit=1)
                if replace_same_key or key not in dict_of_contact:
                    dict_of_contact[key] = value
        list_of_contacts.append(dict_of_contact)

    return list_of_contacts


def list2json(filename: str, list_of_contacts: ContactList) -> None:
    with open(filename + '.json', mode='w') as f:
        json.dump(list_of_contacts, fp=f, indent=4)


def json2list(filename: str) -> ContactList:
    list_of_contacts = []

    with open(filename) as f:
        list_of_contacts = json.load(f)

    return list_of_contacts


def list2csv(filename: str, list_of_contacts: ContactList) -> None:
    headers = headers_of_contacts(list_of_contacts)

    with open(filename + '.csv', mode='w', newline='') as f:
        writer = csv.DictWriter(f,
                                fieldnames=headers,
                                delimiter=',',
                                quotechar='\"',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(list_of_contacts)


def csv2list(filename: str, replace_same_key: bool = False) -> ContactList:
    raw_contacts = []
    list_of_contacts = []

    with open(filename, newline='') as f:
        reader = csv.DictReader(f,
                                delimiter=',',
                                quotechar='\"')
        raw_contacts = list(reader)

    for raw_contact in raw_contacts:
        dict_of_contact = {}
        for key, value in raw_contact.items():
            if value and (replace_same_key or key not in dict_of_contact):
                dict_of_contact[key] = value
        list_of_contacts.append(dict_of_contact)

    return list_of_contacts


def list2vcf(filename: str, list_of_contacts: ContactList) -> None:
    raw_contacts = ''

    for dict_of_contact in list_of_contacts:
        raw_contacts += 'BEGIN:VCARD\n'
        for key, value in dict_of_contact.items():
            raw_contacts += '{}:{}\n'.format(key, value)
        raw_contacts += 'END:VCARD\n'

    with open(filename + '.vcf', mode='w') as f:
        f.write(raw_contacts)


if __name__ == '__main__':
    filename = argv[-1]
    decode = True if '--decode' in argv else False
    reducer = True if '--reducer' in argv else False
    if '--help' in argv or '-h' in argv or len(argv) < 3:
        print(USAGE)
    elif '--version' in argv or '-v' in argv:
        print(VERSION)
    elif '--vcf2csv' in argv:
        list_of_contacts = vcf2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2csv(filename, list_of_contacts)
    elif '--vcf2json' in argv:
        list_of_contacts = vcf2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2json(filename, list_of_contacts)
    elif '--csv2vcf' in argv:
        list_of_contacts = csv2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2vcf(filename, list_of_contacts)
    elif '--csv2json' in argv:
        list_of_contacts = csv2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2json(filename, list_of_contacts)
    elif '--json2vcf' in argv:
        list_of_contacts = json2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2vcf(filename, list_of_contacts)
    elif '--json2csv' in argv:
        list_of_contacts = json2list(filename)
        if decode:
            list_of_contacts = decode_quoted_printable(list_of_contacts)
        if reducer:
            list_of_contacts = reduce_phone_attr(list_of_contacts)
        list2csv(filename, list_of_contacts)
    else:
        print(USAGE)
