# Repository Overview

This repository contains **plint**, a prototype Python tool for proofreading and analyzing patent claims.

## Top-level contents

- `plint.py` – main script implementing all checks.
- `README.md` – documentation describing features and usage.
- `LICENSE` – GNU AGPL v3 license text.
- Data files:
  - `claims.csv` – regex patterns and messages for claim warnings.
  - `title.csv` – patterns used when validating titles.
  - `spec-profanity.csv` – terms to avoid in the specification.
  - `vague-title-words.txt` – list of vague words for titles.
  - `demo-claims.txt` and `demo.json` – minimal example input files.
- `plint-todo.md` – notes on future improvements.

The repository has no subdirectories and no auxiliary build or test scripts.

`README.md` outlines the capabilities of `plint`, such as detecting antecedent basis issues, subjective terms, functional language, and performing simple restriction analysis. The exit statuses documented are 0 for success, 1 for fatal parsing errors, and 2 when warnings are produced.

## Function Reference – `plint.py`

Below is a summary of every function defined in `plint.py`.

### `eprint(*args, **kwargs)`
Prints text either to stderr or to an output file when the `--outfile` option is active. It returns `None`.

### `warn(message, dav_keyword=None)`
Records a warning. Messages may be filtered using regular expressions supplied through command line options. When shown, the warning is printed via `eprint` and `number_of_warnings` is incremented. Any `dav_keyword` is collected for later display in a DAV search string.

### `assert_warn(bool_input, message, dav_keyword=None)`
If `bool_input` evaluates to `False`, calls `warn()` with the provided message. This allows checks to generate warnings without interrupting execution.

### `re_matches(regex, text)`
Performs a case-insensitive regex search. Returns `(False, None)` when the pattern is not found; otherwise returns `(True, matched_string)` where `matched_string` is the text that matched.

### `remove_punctuation(text)`
Removes commas, semicolons and periods from the given string and returns the cleaned text.

### `remove_ab_notation(text)`
Cleans up text that was marked for antecedent basis checking. The function strips various marker characters, removes segments enclosed in backticks (used for comments), trims extra spaces, and returns the cleaned claim text. It verifies that backticks are properly paired.

### `bracket_error_str(claim_number, message, loc, claim_text)`
Utility used when validating marking syntax. It builds an error message indicating the claim number, the problem, the index of the offending character, and a snippet of context.

### `mark_new_element_punctuation(claim_text, claim_number)`
Walks through a claim string and inserts closing `}` brackets at punctuation or pipe characters to terminate new element markers. It also handles `!` to remove accidental characters and validates the balance of `{` and `}`. The modified claim text is returned.

### `mark_old_element_punctuation(claim_text, claim_number)`
Similar to `mark_new_element_punctuation` but operates on old element markers (`[]`). It ensures that closing `]` brackets are inserted appropriately and validates bracket balance.

### `check_marking(claim_text, claim_number)`
Verifies that curly and square brackets in the marked claim text are balanced and not nested. Returns the input text unchanged if no assertion fails.

### `mark_claim_text(claim_text, claim_number, new_elements_set)`
Automatically marks claim text for antecedent basis checking. Steps include:
1. Removing temporary marking characters and ensuring a trailing period.
2. Marking plural starting terms (e.g. “two”) as new elements.
3. Marking singular starting terms (“a”, “the”, “said”) as new or old elements.
4. Converting punctuation into element delimiters with `mark_new_element_punctuation`.
5. Automatically marking repeated elements based on previous occurrences and preventing conflicts between overlapping names.
6. Cleaning up markers, running `mark_old_element_punctuation` and `check_marking`, and returning the fully marked text.

### `powerset(iterable)`
Utility that yields all subsets of the provided iterable, implemented via `itertools.combinations`.

### `load_warnings_file(file_to_load)`
Reads a CSV file containing regex patterns and warning messages. Comments (rows starting with `#`) are skipped unless the `--force` flag is used. The function ensures each row has two columns, checks for duplicate regexes, prints how many rules were loaded/suppressed, and returns a list of dictionaries.

These helper functions support the main procedural logic that parses command line arguments, processes claim text, issues warnings, and performs optional restriction and specification analysis.

