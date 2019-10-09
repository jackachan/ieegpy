#!/usr/bin/python

##################################################################################
# Copyright 2013-19 by the Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##################################################################################

import sys
import argparse
import getpass
from ieeg.auth import Session

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True, help='username')
parser.add_argument('-p', '--password',
                    help='password (will be prompted if omitted)')

parser.add_argument('dataset', help='dataset name')

args = parser.parse_args()

if not args.password:
    args.password = getpass.getpass()

with Session(args.user, args.password) as s:

    # We pick one dataset...
#    ds = s.open_dataset('I004_A0003_D001')
#    ds = s.open_dataset('Study 024')
    ds = s.open_dataset(args.dataset)

    # Iterate through all of the channels and print their metadata
    print('\nBasic Channel Info:')
    for name in ds.get_channel_labels():
        print (ds.get_time_series_details(name))

#    print (ds.get_data(3150000, 50000, ds.get_channel_indices(['LEFT_01', 'LEFT_03', 'LEFT_05', 'LEFT_07'])))
#	print (ds.get_data(3110000, 90000, ds.get_channel_indices(['Grid1', 'Grid2', 'Grid3', 'Grid4'])))
    print('\nAnnotation layers:')
    print(ds.get_annotation_layers())
#    print(ds.get_annotations('Seizures'))
    for key in ds.get_annotation_layers():
        print('Key - ' + key + ' (start_time, end_time in us):')
        print(ds.get_annotations(key))

    print('\nCurrent Montage: ')
    print(ds.get_current_montage())

    s.close_dataset(ds)
