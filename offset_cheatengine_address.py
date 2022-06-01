import os
import time
import io
import argparse

import xml
import xml.etree
import xml.etree.ElementTree


def modify_cheatengine_file(
    input_filepath: str,
    description_name: str,
    new_address_hex: str,
    run=False,
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

    # find the entry with the description
    old_address_hex_str = None
    for cheat_entry_info in cheat_entry_info_list:
        if cheat_entry_info['description'] == description_name:
            old_address_hex_str = cheat_entry_info['address_hex_str']
            break

    if old_address_hex_str is None:
        raise Exception(f'Could not find description: {description_name}')

    # calculate the offset value
    old_address_int = int(old_address_hex_str, 16)
    new_address_int = int(new_address_hex, 16)
    offset_int = new_address_int - old_address_int

    # modify the list
    for cheat_entry_info in cheat_entry_info_list:
        address_hex_str = cheat_entry_info['address_hex_str']
        address_int = int(address_hex_str, 16)
        address_int += offset_int
        address_str = str(hex(address_int))[2:]
        address_str = address_str.upper()
        cheat_entry_info['new_address_hex_str'] = address_str
        print(f'{cheat_entry_info["description"]} {address_hex_str} -> {address_str}')

    # # modify the xml
    # for cheat_entry_info in cheat_entry_info_list:
    #     cheat_entry_info['cheat_entry_ref'].find('Address').text = cheat_entry_info['address_hex_str']

    # # write the xml
    # output_filepath = input_filepath + '.new.ct'
    # xml_tree.write(output_filepath)

    # modify the xml by modifying the text
    content_bs = open(input_filepath, 'rb').read()
    content_str = content_bs.decode('utf-8')
    for cheat_entry_info in cheat_entry_info_list:
        old_address_hex_str = cheat_entry_info['address_hex_str']
        new_address_hex_str = cheat_entry_info['new_address_hex_str']
        content_str = content_str.replace(old_address_hex_str, new_address_hex_str)

    if run:
        # write the xml
        basename, ext = os.path.splitext(input_filepath)
        output_filepath = f'{basename}-{int(time.time())}.ct'
        print(f'writing to {output_filepath}')
        with open(output_filepath, 'wb') as outfile:
            outfile.write(content_str.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('description')
    parser.add_argument('hex')
    parser.add_argument('-r', '--run', action='store_true')

    args = parser.parse_args()
    print('args', args)

    modify_cheatengine_file(
        input_filepath=args.infile,
        description_name=args.description,
        new_address_hex=args.hex,
        run=args.run,
    )


if __name__ == '__main__':
    main()
