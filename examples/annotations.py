'''
 Copyright 2019 Trustees of the University of Pennsylvania

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''
import argparse
import getpass
from ieeg.auth import Session
from ieeg.dataset import Annotation


def print_layers(dataset):
    layer_to_count = dataset.get_annotation_layers()
    print(layer_to_count)


def read(dataset, args):
    """
    Reads annotations from dataset.
    """
    layer_name = args.layer
    layer_to_count = dataset.get_annotation_layers()
    if not layer_name:
        print(layer_to_count)
    else:
        expected_count = layer_to_count[layer_name]
        actual_count = 0
        max_results = None if expected_count < 100 else 100
        call_number = 0
        while actual_count < expected_count:
            annotations = dataset.get_annotations(
                layer_name, first_result=actual_count, max_results=max_results)
            call_number += 1
            actual_count += len(annotations)
            first = annotations[0].start_time_offset_usec
            last = annotations[-1].end_time_offset_usec
            print("got", len(annotations), "annotations on call #",
                  call_number, "covering", first, "usec to", last, "usec")
        print("got", actual_count, "annotations in total")


def add(dataset, args):
    """
    Adds two annotations to the given dataset layer.
    """
    layer_name = args.layer
    if not layer_name:
        print_layers(dataset)
    else:
        annotations = [Annotation(dataset, args.user,
                                  'Test', 'A test annotation', layer_name, 100000, 200100),
                       Annotation(dataset, args.user,
                                  'Test 2', 'A test annotation', layer_name, 200000, 300200)]

        dataset.add_annotations(annotations)
        layer_to_count = dataset.get_annotation_layers()
        print(layer_to_count)


def move(dataset, args):
    """
    Move annotations from one layer to another.
    """
    from_layer = args.from_layer
    to_layer = args.to_layer
    layer_to_count = dataset.get_annotation_layers()
    if not from_layer:
        print(layer_to_count)
    else:
        print('Moving', layer_to_count[from_layer],
              'annotations from', from_layer, 'to', to_layer)
        moved = dataset.move_annotation_layer(from_layer, to_layer)
        print('Moved', moved, 'annotations')
        print(dataset.get_annotation_layers())


def delete(dataset, args):
    """
    Delete annotations from the given layer.
    """
    layer_to_count = dataset.get_annotation_layers()
    layer_name = args.layer
    if not layer_name:
        print(layer_to_count)
    else:
        print('Deleting', layer_to_count[layer_name],
              'annotations from', layer_name)
        deleted = dataset.delete_annotation_layer(layer_name)
        print('Deleted', deleted, 'annotations')
        print(dataset.get_annotation_layers())


def validate(args):
    """
    Do any validation of args that argparse does not provide.
    """
    if hasattr(args, 'from_layer'):
        # Must be a move
        if (args.from_layer and not args.to_layer or args.to_layer and not args.from_layer):
            args.parser.error('Both from_layer and to_layer must be provided.')


def main():
    """
    Parses the command line and dispatches subcommand.
    """

    # create the top-level parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', required=True, help='username')
    parser.add_argument('-p', '--password',
                        help='password (will be prompted if missing')

    parser.add_argument('--host', help='the host')
    parser.add_argument('--use_ssl', action='store_true', default=True,
                        help="Use https, not http. Ignored unless --host is set.")
    parser.add_argument(
        '--port', help='The port. Ignored unless --host is set.')
    parser.set_defaults(parser=parser)

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='<subcommand> -h for subcommand help')

    dataset_parser = argparse.ArgumentParser(add_help=False)
    dataset_parser.add_argument('dataset', help='dataset name')

    layer_parser = argparse.ArgumentParser(add_help=False)
    layer_parser.add_argument(
        'layer', nargs='?', help='Layer name. If missing, print layers in dataset.')

    # The "read" command
    parser_read = subparsers.add_parser('read',
                                        parents=[dataset_parser, layer_parser],
                                        help='Read annotations from the given dataset layer.')
    parser_read.set_defaults(func=read, parser=parser_read)

    # The "add" command
    parser_add = subparsers.add_parser('add',
                                       parents=[dataset_parser, layer_parser],
                                       help='Add two test annotations to the given dataset layer.')
    parser_add.set_defaults(func=add, parser=parser_add)

    # The "delete" command
    parser_delete = subparsers.add_parser('delete',
                                          parents=[
                                              dataset_parser, layer_parser],
                                          help='Delete the  given annotation layer.')
    parser_delete.set_defaults(func=delete, parser=parser_delete)

    # The "move" command
    parser_move = subparsers.add_parser('move',
                                        parents=[dataset_parser],
                                        help='Move annotations from the source layer to the destination layer.')
    parser_move.add_argument(
        'from_layer', nargs='?', metavar='from_layer to_layer', help='source layer')
    parser_move.add_argument(
        'to_layer', nargs='?', metavar='', help='destination layer')
    parser_move.set_defaults(func=move, parser=parser_move)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.error('A subcommand is required.')
    else:
        validate(args)
        if not args.password:
            args.password = getpass.getpass()
        if args.host:
            Session.host = args.host
            if args.port:
                Session.port = args.port
            Session.method = 'https' if args.use_ssl else 'http'

        with Session(args.user, args.password) as session:
            dataset = session.open_dataset(args.dataset)
            args.func(dataset, args)
            session.close_dataset(dataset)


if __name__ == "__main__":
    main()