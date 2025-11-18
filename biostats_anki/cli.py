import argparse
import os
import sys
import json
import pathlib

from .builder import create_deck
from .converter import convert_csv_to_json

def cli_entry():
    
    parser = argparse.ArgumentParser(description='create or convert anki decks from llm-generated files.')
    subparsers = parser.add_subparsers(dest='command', required=True, help='sub-command help')
    
    # --- 'build' command ---
    parser_build = subparsers.add_parser('build', help='build an .apkg file from a v4.0 json file')
    
    parser_build.add_argument(
        'input_jsons',
        type=str,
        nargs='+', # accept one or more inputs
        help='one or more paths to the input v4.0 json files.'
    )
    
    parser_build.add_argument(
        '-o', '--output', 
        type=str, 
        default=None,
        help='optional: exact output file path. '
             'only valid when providing a single input file.'
    )
    
    parser_build.add_argument(
        '-d', '--dir',
        type=str, 
        default=os.getcwd(),
        help='directory to save the output .apkg file(s). '
             'defaults to the current working directory.'
    )
    
    # --- 'convert' command ---
    parser_convert = subparsers.add_parser('convert', help='convert a legacy csv file to a v4.0 json file')
    
    parser_convert.add_argument(
        'input_csvs',
        type=str, 
        nargs='+', # accept one or more inputs
        help='one or more paths to the legacy input csv files.'
    )
    
    parser_convert.add_argument(
        '-o', '--output', 
        type=str, 
        default=None,
        help='optional: exact output file path. '
             'only valid when providing a single input file.'
    )
    
    parser_convert.add_argument(
        '-d', '--dir',
        type=str, 
        default=os.getcwd(),
        help='directory to save the output .json file(s). '
             'defaults to the current working directory.'
    )
    
    # --- argument processing ---
    
    args = parser.parse_args()
    
    if args.command == 'build':
        
        # validation check
        if len(args.input_jsons) > 1 and args.output:
            print("error: --output flag can only be used with a single input file.", file=sys.stderr)
            sys.exit(1)
            
        for input_json_path in args.input_jsons:
            input_path = os.path.abspath(input_json_path)
            
            # derive deck name from json content (must be done per file)
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    deck_data = json.load(f)
                source_id = deck_data['source_id']
                unit_id = deck_data['unit_id']
                deck_name = f"{source_id}-{unit_id}"
            except Exception as e:
                print(f"error reading deck name from json file: {input_path}", file=sys.stderr)
                print(f"error: {e}", file=sys.stderr)
                print("please ensure input json is valid and contains 'source_id' and 'unit_id'.", file=sys.stderr)
                continue # skip this file, move to next

            # determine output path
            if args.output:
                # this branch only runs if len(args.input_jsons) == 1
                final_output_path = os.path.abspath(args.output)
            else:
                # default behavior: use deck name in the specified dir
                output_filename = f"{deck_name}.apkg"
                final_output_path = os.path.abspath(os.path.join(args.dir, output_filename))

            print(f"--- building deck: {deck_name} ---")
            create_deck(input_path, final_output_path, deck_name)
            print("---------------------------------")
        
    elif args.command == 'convert':
        
        # validation check
        if len(args.input_csvs) > 1 and args.output:
            print("error: --output flag can only be used with a single input file.", file=sys.stderr)
            sys.exit(1)

        for input_csv_path in args.input_csvs:
            input_path = os.path.abspath(input_csv_path)

            # determine output path
            if args.output:
                # this branch only runs if len(args.input_csvs) == 1
                final_output_path = os.path.abspath(args.output)
            else:
                # default behavior: use {basename}.json in the specified dir
                base = os.path.basename(input_path)
                filename_no_ext = os.path.splitext(base)[0]
                output_filename = f"{filename_no_ext}.json"
                final_output_path = os.path.abspath(os.path.join(args.dir, output_filename))

            print(f"--- converting file: {input_path} ---")
            convert_csv_to_json(input_path, final_output_path)
            print("-----------------------------------")