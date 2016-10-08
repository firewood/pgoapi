#!/usr/bin/env python
"""
dump iv of all pokemons
"""

import os
import sys
import codecs
import json
import time
import pprint
import logging
import getpass
import argparse

# add directory of this file to PATH, so that the package will be found
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# import Pokemon Go API lib
from pgoapi import pgoapi
from pgoapi import utilities as util

def die(*args):
    print("".join(map(str, args)))
    sys.exit()

def init_config():
    config_file = "config.json"
    if not os.path.isfile(config_file):
        die("Not found: " + config_file)

    config = json.load(open(config_file, 'r'))

    for key in ["auth_service", "location", "username", "password"]:
        if key not in config:
            die(key + " not found in: " + config_file)

    return config

def load_monsters():
    monsters_file = 'pokemon.ja.json'
    if not os.path.isfile(monsters_file):
        return {}
    return json.load(codecs.open(monsters_file, 'r', 'utf-8'))

def get_monster_name(monsters, id):
    if id in monsters:
        return monsters[id]
    return u'?'

def extract_pokemons(inventories):
    result = []
    for inventory in inventories:
        if 'inventory_item_data' in inventory:
            inventory_item_data = inventory['inventory_item_data']
            if 'pokemon_data' in inventory_item_data:
                result.append(inventory_item_data['pokemon_data'])
    return result

def format_iv(attack, defense, stamina):
    return ('0' + str(attack + defense))[-2:] + ('0' + str(stamina))[-2:]

def pretty_print_inventory(response_dict, monsters):
    inventories = response_dict['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
    pokemons = extract_pokemons(inventories)
    sorted_pokemons = sorted(pokemons, key=lambda x: -x['creation_time_ms'])

#    print(format(pprint.PrettyPrinter(indent=3).pformat(sorted_pokemons)))

    for pokemon in sorted_pokemons:
        id = pokemon.get('pokemon_id', -1)
        name = pokemon.get('nickname', get_monster_name(monsters, str(id)))
        attack = pokemon.get('individual_attack', 0)
        defense = pokemon.get('individual_defense', 0)
        stamina = pokemon.get('individual_stamina', 0)
        cp = pokemon.get('cp', -1)
        if cp > 0:
#            print(u','.join(map(unicode, [format_iv(attack, defense, stamina), attack, defense, stamina, cp, name])).encode('utf-8'))
            sys.stdout.buffer.write(u'{0:0>4} {1:>2} {2:>2} {3:>2} {4:>4} {5}\n'.format((attack + defense) * 100 + stamina, attack, defense, stamina, cp, name).encode('utf-8'))
  

def main():
    config = init_config()
    monsters = load_monsters()

    # instantiate pgoapi
    api = pgoapi.PGoApi()

    # parse position
    position = util.get_pos_by_name(config["location"])
    if not position:
        die('Your given location could not be found by name')

    # set player position on the earth
    api.set_position(*position)

    if not api.login(config["auth_service"], config["username"], config["password"], app_simulation = True):
        return

    # get inventory
    req = api.create_request()
    req.get_inventory()
    response_dict = req.call()
    pretty_print_inventory(response_dict, monsters)

if __name__ == '__main__':
    main()
