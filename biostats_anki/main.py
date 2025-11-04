import genanki
import csv
import pathlib
import hashlib
import argparse
import sys
import os

# --- Model & Field Definitions (Hardcoded) ---

# fields must match csv columns *exactly* in order
MODEL_FIELDS = [
    {'name': 'ID'},
    {'name': 'Context'},
    {'name': 'Topic'},
    {'name': 'Molecule'},
    {'name': 'Card_Type'},
    {'name': 'Question'},
    {'name': 'Answer'},
    {'name': 'Extra_Context'},
    {'name': 'Source'},
]

MODEL_C1_ID = 1607934231  # arbitrary unique id
MODEL_C1_NAME = 'Biostats-PhD-C1 (Q/A)'
MODEL_C2_ID = 1607934232  # arbitrary unique id
MODEL_C2_NAME = 'Biostats-PhD-C2 (Cloze)'

# --- Helper Functions ---

def read_file(path: pathlib.Path) -> str:
    """reads the content of a file and returns it as a string."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"error: template file not found at {path}", file=sys.stderr)
        print("ensure 'anki-card-templates' dir is inside the 'biostats_anki' package dir.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error reading file {path}: {e}", file=sys.stderr)
        sys.exit(1)

def parse_html_template(html_content: str) -> (str, str):
    """parses the HTML content to find '### FRONT' and '### BACK' sections."""
    try:
        front = html_content.split('### FRONT')[1].split('### BACK')[0].strip()
        back = html_content.split('### BACK')[1].strip()
        return front, back
    except (IndexError, AttributeError):
        print("error: html template is malformed.", file=sys.stderr)
        print("ensure it contains '### FRONT' and '### BACK' separators.", file=sys.stderr)
        sys.exit(1)

def generate_id_from_name(name: str) -> int:
    """creates a stable, deck-specific integer id from a string name."""
    hash_val = hashlib.sha256(name.encode('utf-8')).hexdigest()
    return int(hash_val[:10], 16)

def create_deck(input_csv_path: str, deck_name: str, output_apkg_path: str):
    """
    main logic to generate the anki deck.
    """
    
    package_dir = pathlib.Path(__file__).resolve().parent
    templates_dir = package_dir / 'anki-card-templates'
    
    css_path = templates_dir / 'css-biostats-phd_card.css'
    c1_html_path = templates_dir / 'C1_biostats-phd_card.html'
    c2_html_path = templates_dir / 'C2_biostats-phd_card.html'

    print("loading templates...")
    css_content = read_file(css_path)
    c1_html_content = read_file(c1_html_path)
    c2_html_content = read_file(c2_html_path)
    
    
    c1_front, c1_back = parse_html_template(c1_html_content)
    c2_front, c2_back = parse_html_template(c2_html_content)

    # define model 1: standard q/a
    model_c1 = genanki.Model(
        MODEL_C1_ID,
        MODEL_C1_NAME,
        fields=MODEL_FIELDS,
        templates=[{'name': 'Card 1', 'qfmt': c1_front, 'afmt': c1_back}],
        css=css_content
    )

    # define model 2: cloze
    model_c2 = genanki.Model(
        MODEL_C2_ID,
        MODEL_C2_NAME,
        fields=MODEL_FIELDS,
        templates=[{'name': 'Cloze', 'qfmt': c2_front, 'afmt': c2_back}],
        css=css_content,
        model_type=genanki.Model.CLOZE
    )
    
    deck_id = generate_id_from_name(deck_name)
    my_deck = genanki.Deck(deck_id, deck_name)
    
    print(f"processing csv file: {input_csv_path}")

    notes_added = 0
    cloze_notes = 0
    qa_notes = 0
    
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if not row:
                    continue  # skip empty rows
                
                if len(row) != 9: # changed from 8 to 9
                    print(f"warning: skipping malformed row. expected 9 fields, got {len(row)}: {row}", file=sys.stderr)
                    continue
                
                field_data = row
                question_content = row[5] # changed from 4 to 5
                
                if '{{c1::' in question_content:
                    note = genanki.Note(model=model_c2, fields=field_data)
                    cloze_notes += 1
                else:
                    note = genanki.Note(model=model_c1, fields=field_data)
                    qa_notes += 1
                    
                my_deck.add_note(note)
                notes_added += 1

    except FileNotFoundError:
        print(f"error: input csv file not found at {input_csv_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"an error occurred while reading the csv: {e}", file=sys.stderr)
        sys.exit(1)

    
    if notes_added > 0:
        print("packaging deck...")
        
        output_dir = os.path.dirname(output_apkg_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        genanki.Package(my_deck).write_to_file(output_apkg_path)
        print(f"\nsuccess! deck '{deck_name}' created.")
        print(f"  total notes: {notes_added}")
        print(f"  q/a notes:   {qa_notes}")
        print(f"  cloze notes: {cloze_notes}")
        print(f"  output file: {output_apkg_path}")
    else:
        print("no notes were found in the csv. no deck was created.")

def cli_entry():
    
    parser = argparse.ArgumentParser(description='create anki decks from llm-generated csvs.')
    
    parser.add_argument(
        'input_csv', 
        type=str, 
        help='path to the input csv file.'
    )
    
    parser.add_argument(
        '--name', 
        type=str, 
        required=True, 
        help='the desired name for the anki deck (also used for the output filename).'
    )
    
    output_group = parser.add_mutually_exclusive_group()
    
    output_group.add_argument(
        '-o', '--output', 
        type=str, 
        default=None,
        help='optional: exact path for the output .apkg file (e.g., /path/to/my_deck.apkg). '
             'this overrides --output_dir.'
    )
    
    output_group.add_argument(
        '-od', '--output_dir', 
        type=str, 
        default=os.getcwd(),
        help='optional: directory to save the .apkg file. '
             'defaults to the current working directory.'
    )
    
    args = parser.parse_args()
    
    
    input_path = os.path.abspath(args.input_csv)
    
    if args.output:
        # user specified an exact file path
        output_path = args.output
    else:
        # user specified a directory (or used the default cwd)
        # sanitize deck name for file output
        sane_filename = "".join(c for c in args.name if c.isalnum() or c in ('_', '-')).rstrip().replace(' ', '_')
        output_filename = f"{sane_filename}.apkg"
        output_path = os.path.join(args.output_dir, output_filename)

    final_output_path = os.path.abspath(output_path)
    
    create_deck(input_path, args.name, final_output_path)

if __name__ == "__main__":
    cli_entry()