#!/usr/bin/python

# e.g. python GetDataToFile.py -u jackchan -p innCe1212J "Study 024" 230603765000 600000000 test_out1
# all time values are in us
# duration (the 2nd last argument) affect the size of file
# duration cannot be too large for the response of HTTP post has some limitations
# 10min of duration, i.e. 600000000, still works as tested

import argparse
import getpass
from ieeg.auth import Session


def main():
    """
    Prints requested data
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', required=True, help='username')
    parser.add_argument('-p', '--password',
                        help='password (will be prompted if omitted)')

    parser.add_argument('dataset', help='dataset name')
    parser.add_argument('start', type=int, help='start offset in usec')
    parser.add_argument('duration', type=int, help='number of usec to request')
    parser.add_argument('filename', help='output file name')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass()

    outfile = open(args.filename, 'w+')

    with Session(args.user, args.password) as session:
        dataset_name = args.dataset
        dataset = session.open_dataset(dataset_name)
        channels = list(range(len(dataset.ch_labels)))
        outfile.write('#Channel labels\n')
        for ch_name in dataset.get_channel_labels():
            outfile.write(str(ch_name)+', ')
        outfile.write('\n')
        outfile.write('#Annotation (us)\n')
        for key in dataset.get_annotation_layers():
            for anno in dataset.get_annotations(key):
                outfile.write(str(anno)+', ')
            outfile.write('\n')

        raw_data = dataset.get_data(args.start, args.duration, channels)

        sample_rate = raw_data.shape[0]/(args.duration/(1000000))

        outfile.write('#Raw EEG data (uV) - row: the readings of that time from all channels\n')
        outfile.write('#Starting time (us): '+str(args.start) + '\n')
        outfile.write('#Total duration (us): '+str(args.duration) + '\n')
        outfile.write('#Total number of channels: '+str(raw_data.shape[1]) + '\n')
        outfile.write('#Total number of samples for each channel: '+str(raw_data.shape[0]) + '\n')
        outfile.write('#Sampling rate (Hz): '+str(sample_rate) + '\n')

        for row in raw_data:
            for elem in row:
                outfile.write(str(elem)+', ')
            outfile.write('\n')

        session.close_dataset(dataset_name)

    outfile.close()

if __name__ == "__main__":
    main()
