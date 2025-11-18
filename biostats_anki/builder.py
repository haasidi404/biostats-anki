import genanki
import json
import os
import sys
import pathlib

# relative imports from within the package
from .models import MODEL_FIELDS, MODEL_C1_ID, MODEL_C1_NAME, MODEL_C2_ID, MODEL_C2_NAME
from .utils import read_file, parse_html_template, generate_id_from_name, convert_legacy_latex

def create_deck(input_json_path: str, output_apkg_path: str, deck_name: str):
    """
    main logic to generate the anki deck from a v4.0 json file.
    """
    
    # get the path to the installed package's directory
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
    
    print(f"processing json file: {input_json_path}")

    notes_added = 0
    cloze_notes = 0
    qa_notes = 0
    
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            deck_data = json.load(f)
            
        for card in deck_data['cards']:
            
            # apply latex conversion to relevant fields
            question_content = convert_legacy_latex(card.get('Question', ''))
            answer_content = convert_legacy_latex(card.get('Answer', ''))
            extra_context_content = convert_legacy_latex(card.get('Extra_Context', ''))

            # fields must be in the *exact* order defined in MODEL_FIELDS
            field_data = [
                card.get('ID', ''),
                card.get('Context', ''),
                card.get('Topic', ''),
                card.get('Molecule_ID', ''),
                card.get('Card_Type', ''),
                question_content,
                answer_content,
                extra_context_content,
                card.get('Source', '')
            ]
            
            if '{{c1::' in question_content:
                note = genanki.Note(model=model_c2, fields=field_data)
                cloze_notes += 1
            else:
                note = genanki.Note(model=model_c1, fields=field_data)
                qa_notes += 1
                
            my_deck.add_note(note)
            notes_added += 1

    except FileNotFoundError:
        print(f"error: input json file not found at {input_json_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"error: could not parse json file. file may be malformed: {input_json_path}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"error: json file is missing expected key: {e}. is it a valid v4.0 deck file?", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"an error occurred while processing the json file: {e}", file=sys.stderr)
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
        print("no notes were found in the json. no deck was created.")