import csv
import json
import re
from sys import argv
from typing import Dict, List

Contact = Dict[str, str]
ContactList = List[Contact]


CONVERSION = '''
conversion:
--vcf2csv\t\t From VCard to CSV
--vcf2json\t\t From VCard to JSON
--csv2vcf\t\t From CSV to VCard
--csv2json\t\t From CSV to JSON
--json2vcf\t\t From JSON to VCard
--json2csv\t\t From JSON to CSV
'''
USAGE = ('usage: python3 {} <conversion> <filename>\n{}'
         .format(argv[0], CONVERSION))
VERSION = '0.1'


def headers_of_contacts(list_of_contacts: ContactList) -> List[str]:
    headers = []

    for dict_of_contact in list_of_contacts:
        contact_keys = dict_of_contact.keys()
        for key in contact_keys:
            if key not in headers:
                headers.append(key)

    return headers


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
    if '--help' in argv or '-h' in argv or len(argv) < 3:
        print(USAGE)
    elif '--version' in argv or '-v' in argv:
        print(VERSION)
    elif '--vcf2csv' in argv:
        list2csv(filename, vcf2list(filename))
    elif '--vcf2json' in argv:
        list2json(filename, vcf2list(filename))
    elif '--csv2vcf' in argv:
        list2vcf(filename, csv2list(filename))
    elif '--csv2json' in argv:
        list2json(filename, csv2list(filename))
    elif '--json2vcf' in argv:
        list2vcf(filename, json2list(filename))
    elif '--json2csv' in argv:
        list2csv(filename, json2list(filename))
    else:
        print(USAGE)
