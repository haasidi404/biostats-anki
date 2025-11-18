# Biostats Anki Deck Builder (badeck)

`badeck` is a command-line tool for building Anki .apkg files from structured JSON input. It is designed specifically for the "Biostats-PhD-v3" Anki note types (Q/A and Cloze) and includes a utility for migrating legacy CSV-based decks to the new JSON format.

The tool is part of a larger workflow where a Unified Knowledge Inventory (UKI) is first processed by an LLM to generate a v4.0 JSON file, which this tool then consumes.

---

## Features

* **Build .apkg Decks**: Converts v4.0 JSON files into ready-to-import Anki decks.
* **Custom Note Types**: Uses the `Biostats-PhD-C1` (Q/A) and `Biostats-PhD-C2` (Cloze) note types, with bundled HTML/CSS templates.
* **Legacy CSV Conversion**: Includes a `convert` command to migrate old 9-column CSV decks to the new v4.0 JSON format.
* **LaTeX Normalization**: Automatically converts legacy `\vect{}` and `\mat{}` LaTeX macros to the standard `\boldsymbol{...}` during conversion.

---

## Installation

This project is packaged using `pyproject.toml`. You can install it locally using pip:

```bash
# clone the repository (if you haven't already)
git clone [https://github.com/yourusername/biostats_anki.git](https://github.com/yourusername/biostats_anki.git)
cd biostats_anki

# install the package in editable mode
pip install -e .
````

This makes the `badeck` command-line tool available in your environment.

-----

## Usage

The tool provides two main commands: `build` and `convert`.

### 1\. badeck build

This command builds one or more `.apkg` deck files from v4.0 JSON inputs.

```bash
# get help for the build command
badeck build --help
```

```text
usage: badeck build [-h] [-o OUTPUT] [-d DIR] input_jsons [input_jsons ...]

positional arguments:
  input_jsons           one or more paths to the input v4.0 json files.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        optional: exact output file path. only valid when
                        providing a single input file.
  -d DIR, --dir DIR     directory to save the output .apkg file(s).
                        defaults to the current working directory.
```

**Examples:**

```bash
# build a single deck in the current directory
badeck build ./my_deck.json

# build a single deck and specify the output path
badeck build ./my_deck.json -o /path/to/AM751-L01.apkg

# build multiple decks, saving them to the 'output_decks' directory
badeck build ./deck1.json ./deck2.json -d ./output_decks
```

### 2\. badeck convert

This command converts one or more legacy 9-column CSV files into the v4.0 JSON format.

```bash
# get help for the convert command
badeck convert --help
```

```text
usage: badeck convert [-h] [-o OUTPUT] [-d DIR] input_csvs [input_csvs ...]

positional arguments:
  input_csvs            one or more paths to the legacy input csv files.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        optional: exact output file path. only valid when
                        providing a single input file.
  -d DIR, --dir DIR     directory to save the output .json file(s).
                        defaults to the current working directory.
```

**Examples:**

```bash
# convert a single csv, saving it as 'legacy_deck.json' in the current directory
badeck convert ./legacy_deck.csv

# convert a single csv and specify the output name/path
badeck convert ./legacy_deck.csv -o /path/to/new_deck_v4.json

# convert multiple csvs, saving them to the 'json_outputs' directory
badeck convert ./deck1.csv ./deck2.csv -d ./json_outputs
# output: ./json_outputs/deck1.json, ./json_outputs/deck2.json
```

-----

## Input JSON Format (v4.0)

The `build` command expects a JSON file with a specific structure. The file must contain root-level `source_id` and `unit_id` keys, and an array of `cards`.

**Example (`anki_deck_v4.json`):**

```json
{
  "schema_version": "4.0",
  "source_id": "AM751",
  "unit_id": "L04",
  "cards": [
    {
      "ID": "AM751.L04-001",
      "Context": "Linear Models",
      "Topic": "Projections",
      "Molecule_ID": "DEF.AM751-L04.01",
      "Card_Type": "Atomic Q/A",
      "Question": "What are the two defining properties of an <b>orthogonal projection matrix</b> $\\boldsymbol{P}$?",
      "Answer": "1. It is <b>symmetric</b> ($\\boldsymbol{P}' = \\boldsymbol{P}$)<br>2. It is <b>idempotent</b> ($\\boldsymbol{P}^2 = \\boldsymbol{P}$)",
      "Extra_Context": "These properties are fundamental and lead to many other results in OLS.",
      "Source": "AM751-L04"
    },
    {
      "ID": "AM751.L04-002",
      "Context": "Linear Models",
      "Topic": "Projections",
      "Molecule_ID": "DEF.AM751-L04.01",
      "Card_Type": "Atomic Cloze",
      "Question": "An orthogonal projection matrix $\\boldsymbol{P}$ is idempotent, meaning {{c1::$\\boldsymbol{P}^2 = \\boldsymbol{P}$}}.",
      "Answer": "",
      "Extra_Context": "",
      "Source": "AM751-L04"
    }
  ]
}
```

-----

## Anki Note Types

This tool relies on two specific Anki note types being present in your collection. The required fields are:

  * ID
  * Context
  * Topic
  * Molecule\_ID
  * Card\_Type
  * Question
  * Answer
  * Extra\_Context
  * Source

The HTML/CSS templates for these note types are included in the `biostats_anki/anki-card-templates` directory.