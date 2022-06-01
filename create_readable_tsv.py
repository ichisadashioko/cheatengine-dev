import os
import time
import io
import argparse

import xml
import xml.etree
import xml.etree.ElementTree


def create_readable_tsv(
    input_filepath: str,
):
    xml_tree = xml.etree.ElementTree.parse(input_filepath)

    # find all <CheatEntry> elements
    cheat_entries = xml_tree.findall('.//CheatEntry')
    # filter for only elements with <Address>
    cheat_entries = [
        cheat_entry
        for cheat_entry in cheat_entries
        if cheat_entry.find('Address') is not None
    ]

    cheat_entry_info_list = []
    # store (description, address, cheat_entry_ref)
    for cheat_entry in cheat_entries:
        description = None
        description_element = cheat_entry.find('Description')
        if description_element is not None:
            description = description_element.text
            # remove the quotes
            # check the string length
            if len(description) > 1:
                description = description[1:-1]
            else:
                print(f'Description is too short: {description}')
        address_element = cheat_entry.find('Address')
        if address_element is not None:
            address = address_element.text
            cheat_entry_info = {
                'description': description,
                'address_hex_str': address,
                'cheat_entry_ref': cheat_entry,
            }
            cheat_entry_info_list.append(cheat_entry_info)
        else:
            print('no address in this entry')

    basename, ext = os.path.splitext(input_filepath)
    output_filepath = f'{basename}.tsv'
    print(f'output_filepath: {output_filepath}')

    with open(output_filepath, 'wb') as outfile:
        # write data
        for cheat_entry_info in cheat_entry_info_list:
            description = cheat_entry_info['description']
            address_hex_str = cheat_entry_info['address_hex_str']

            # write data
            outfile.write(b'\t'.join([
                description.encode('utf-8'),
                address_hex_str.encode('utf-8'),
            ]))

            outfile.write(b'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')

    args = parser.parse_args()
    print('args', args)

    create_readable_tsv(
        input_filepath=args.infile,
    )


if __name__ == '__main__':
    main()
