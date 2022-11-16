 # Copyright 2020 Hewlett Packard Enterprise Development LP
 #
 # Licensed under the Apache License, Version 2.0 (the "License"); you may
 # not use this file except in compliance with the License. You may obtain
 # a copy of the License at
 #
 #      http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 # License for the specific language governing permissions and limitations
 # under the License.

# -*- coding: utf-8 -*-
"""
An example of retrieving bios settings
"""

import sys
import json
import argparse
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError
global DISABLE_RESOURCE_DIR
from get_resource_directory import get_resource_directory
from ilorest_util import get_gen

def get_bios_setting(_redfishobj):

    bios_uri = None
    bios_data = None
    resource_instances = get_resource_directory(_redfishobj)
    if DISABLE_RESOURCE_DIR or not resource_instances:
        #if we do not have a resource directory or want to force it's non use to find the
        #relevant URI
        systems_uri = _redfishobj.root.obj['Systems']['@odata.id']
        systems_response = _redfishobj.get(systems_uri)
        systems_members_uri = next(iter(systems_response.obj['Members']))['@odata.id']
        systems_members_response = _redfishobj.get(systems_members_uri)
        bios_uri = systems_members_response.obj['Bios']['@odata.id']
        bios_data = _redfishobj.get(bios_uri)
    else:
        #Use Resource directory to find the relevant URI
        for instance in resource_instances:
            if '#Bios.' in instance['@odata.type']:
                bios_uri = instance['@odata.id']
                bios_data = _redfishobj.get(bios_uri)
                break

    if bios_data:
        print("\n\nShowing bios attributes before changes:\n\n")
        print(json.dumps(bios_data.dict, indent=4, sort_keys=True))

def get_schema(_redfishobj):
    schema_members_uris = []
    schema_members_expanded = {}

    schema_uri = _redfishobj.root.obj['JsonSchemas']['@odata.id']
    schema_response = _redfishobj.get(schema_uri)
    schema_members_uris = schema_response.obj['Members']
    for member in schema_members_uris:
        data = _redfishobj.get(member['@odata.id']).dict
        instance_id = data['Location'].index(next(iter(data['Location'])))
        schema_uri = data['Location'][instance_id]['Uri']
        schema = _redfishobj.get(schema_uri).dict
        #I am just replacing the URI link for the sub-schema with the actual schema. You will
        #see EVERYTHING
        _tmp = {schema_uri + ' ->': schema}
        data['Location'][instance_id]['Uri'] = _tmp
        schema_members_expanded[member['@odata.id']] = data

    print(json.dumps(schema_members_expanded, indent=4, sort_keys=True))

def display_ilo_user_account(_redfishobj):

    account_collection_uri = None
    account_service_uri = _redfishobj.root.obj['AccountService']['@odata.id']
    account_service_response = _redfishobj.get(account_service_uri)
    account_collection_uri = account_service_response.obj['Accounts']['@odata.id']
    # print(json.dumps(account_collection_uri, indent=4, sort_keys=True))
        
    account_uris = redfish_obj.get(account_collection_uri)
    for account_uri in account_uris.dict['Members']:
        account = redfish_obj.get(account_uri['@odata.id'])
    #    print(json.dumps(account, indent=4, sort_keys=True))
        print(account.dict['UserName'])

if __name__ == "__main__":
 
    SYSTEM_URL = "https://10.10.109.56"
    LOGIN_ACCOUNT = "hpadmin"
    LOGIN_PASSWORD = "atlpresales"

    DISABLE_RESOURCE_DIR = False

    try:
        # Create a Redfish client object
        redfish_obj = RedfishClient(base_url=SYSTEM_URL, username=LOGIN_ACCOUNT, password=LOGIN_PASSWORD)
        redfish_obj.login()
    except ServerDownOrUnreachableError as excp:
        sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
        sys.exit()

    # get_bios_setting(redfish_obj)
    display_ilo_user_account(redfish_obj)

    redfish_obj.logout()