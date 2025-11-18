import csv
import json
import sys

from .utils import convert_legacy_latex

def convert_csv_to_json(input_csv_path: str, output_json_path: str):
    """
    converts a legacy 9-column csv to the new v4.0 json format,
    including updating latex macros.
    """
    print(f"converting legacy csv {input_csv_path} to json...")
    cards = []
    source_id = "unknown"
    unit_id = "unknown"
    
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for i, row in enumerate(reader):
                if not row:
                    continue  # skip empty rows
                
                if len(row) != 9:
                    print(f"warning: skipping malformed row {i+1}. expected 9 fields, got {len(row)}.", file=sys.stderr)
                    continue
                
                # extract source from first row
                if i == 0:
                    source_full = row[8] # 'source' field
                    if '-' in source_full:
                        parts = source_full.split('-', 1)
                        source_id = parts[0]
                        unit_id = parts[1]
                    else:
                        source_id = source_full
                        unit_id = "L01" # fallback
                    print(f"inferred source_id: '{source_id}', unit_id: '{unit_id}'")

                # apply latex conversion to relevant fields
                question_content = convert_legacy_latex(row[5])
                answer_content = convert_legacy_latex(row[6])
                extra_context_content = convert_legacy_latex(row[7])

                card = {
                    "ID": row[0],
                    "Context": row[1],
                    "Topic": row[2],
                    "Molecule_ID": row[3],
                    "Card_Type": row[4],
                    "Question": question_content,
                    "Answer": answer_content,
                    "Extra_Context": extra_context_content,
                    "Source": row[8]
                }
                cards.append(card)
        
        output_data = {
            "schema_version": "4.0",
            "source_id": source_id,
            "unit_id": unit_id,
            "cards": cards
        }
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
            
        print(f"success! converted {len(cards)} cards.")
        print(f"output file: {output_json_path}")

    except FileNotFoundError:
        print(f"error: input csv file not found at {input_csv_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"an error occurred while converting the csv: {e}", file=sys.stderr)
        sys.exit(1)