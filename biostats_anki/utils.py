import pathlib
import sys
import hashlib
import re

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

def convert_legacy_latex(text: str) -> str:
    """
    updates latex formatting:
    1. converts $$...$$ to \\[...\\] (display math)
    2. converts $...$ to \\(...\\) (inline math)
    3. converts legacy \\vect{} and \\mat{} macros to standard \\boldsymbol{}.
    """
    if not text:
        return ""

    # 1. convert display math: $$...$$ -> \[...\]
    # uses dotall flag so the dot matches newlines (for multiline equations)
    text = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', text, flags=re.DOTALL)

    # 2. convert inline math: $...$ -> \(...\)
    # uses negative lookbehind/lookahead to avoid matching escaped \$
    # converts only if $ is not preceded by a backslash
    text = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', r'\\(\1\\)', text, flags=re.DOTALL)

    # 3. convert legacy macros
    # convert \vect{...} to \boldsymbol{...}
    text = re.sub(r'\\vect\{(.+?)\}', r'\\boldsymbol{\1}', text)
    # convert \mat{...} to \boldsymbol{...}
    text = re.sub(r'\\mat\{(.+?)\}', r'\\boldsymbol{\1}', text)
    
    return text