import json
import os

import CloudFlare
import requests


def main():
    ''' 
    This program migrates settings from one zone to another.
    Follow below link to see how to configure credentials...
    https://github.com/cloudflare/python-cloudflare#providing-cloudflare-username-and-api-key
    '''
    cf = CloudFlare.CloudFlare(profile="admin")
    zone_list = cf.zones.get()

    ''' Create objects for source and destination zones '''
    src_zone_dict = select_zone("Source zone: ", zone_list)
    id = src_zone_dict['id']
    message = "Destination zone: "
    while id == src_zone_dict['id']:
        dst_zone_dict = select_zone(message, zone_list)
        id = dst_zone_dict['id']
        if id == src_zone_dict['id']: 
            message = "Source and destination can't be the same! Destination zone: "
    # print(json.dumps(src_zone_dict, indent=2))
    # print(json.dumps(dst_zone_dict, indent=2))

    clear()
    if input("Copy DNS? <y/N>: ").lower() in ['y', 'yes']:
        copy_dns_records(cf, src_zone_dict, dst_zone_dict)
    else:
        print("Not copying DNS records...")

    if input("Copy Page Rules? <y/N>: ").lower() in ['y', 'yes']:
        copy_page_rules(cf, src_zone_dict, dst_zone_dict)
    else:
        print("Not copying page rules...")

    return


def copy_page_rules(cf, src_zone_dict, dst_zone_dict):
    ''' Copy page rules from Source Zone to Destination Zone '''
    page_rules_list = cf.zones.pagerules.get(src_zone_dict['id'])
    clear()
    for pagerule in page_rules_list:
        print("SRC: " + pagerule['targets'][0]['constraint']['value'])
        if src_zone_dict['name'] in pagerule['targets'][0]['constraint']['value']:
            pagerule['targets'][0]['constraint']['value'] = pagerule['targets'][0]['constraint']['value'].replace(src_zone_dict['name'], dst_zone_dict['name'])
        newrule = {"targets":pagerule['targets'],"actions":pagerule['actions'],"priority":pagerule['priority'],"status":pagerule['status']}
        result = cf.zones.pagerules.post(dst_zone_dict['id'], data=newrule)
        print("DST: " + pagerule['targets'][0]['constraint']['value'] + "\n")
    # print(json.dumps(page_rules_list, indent=2))
    return 


def copy_dns_records(cf, src_zone_dict, dst_zone_dict):
    ''' Copy DNS records from Source Zone to Destination Zone '''
    dns_record_list = cf.zones.dns_records.get(src_zone_dict['id'])
    clear()
    for dns_record in dns_record_list:
        print("SRC: " + dns_record['type'] + (8 - len(dns_record['type'])) * " " + dns_record['name'] + "    " + dns_record['content'])
        if src_zone_dict['name'] in dns_record['name']:
            dns_record['name'] = dns_record['name'].replace(src_zone_dict['name'], dst_zone_dict['name'])
        if src_zone_dict['name'] in dns_record['content']:
            dns_record['content'] = dns_record['content'].replace(src_zone_dict['name'], dst_zone_dict['name'])
        result = cf.zones.dns_records.post(dst_zone_dict['id'], data=dns_record)
        print("DST: " + dns_record['type'] + (8 - len(dns_record['type'])) * " " + dns_record['name'] + "    " + dns_record['content'] + "\n")
    # print(json.dumps(dns_record_list, indent=2))
    return 


def select_zone(message, zone_list):
    '''
    Interactive function that lists all zones and returns the selected zone object.
    '''
    zone_selection = 0
    while not ((zone_selection <= len(zone_list)) and (zone_selection > 0)):
        print_zones(zone_list)
        i = input(message)
        try:
            zone_selection = int(i)
        except ValueError:
            message = "Try a number between 1 and " + str(len(zone_list)) + ": "
    return (zone_list[zone_selection - 1])
   

def print_zones(zone_list):
    clear()
    print("Zones:")
    for zone in zone_list:
        print(str(zone_list.index(zone) + 1) + ". " + zone['name'])
    return
   

def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear') 


if __name__ == "__main__":
    main()
