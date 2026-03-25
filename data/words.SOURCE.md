# words.txt source

`data/words.txt` is generated from the SCOWL (English Speller Database) project:

- Repository: `https://github.com/en-wl/wordlist`
- Project name: SCOWLv2 / English Speller Database
- Copyright: Kevin Atkinson and contributors

This repo currently uses a generated American English spell-check word list created from SCOWL with:

```bash
./scowl --db scowl.db word-list 60 A 1 --deaccent > wl.txt
```

The generated list was then copied into this repository as:

- [words.txt](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/words.txt)

License note:

SCOWL's `Copyright` file grants permission to use, copy, modify, distribute, and sell the database and word lists created from it without fee, provided the copyright notice and permission notice are preserved in supporting documentation.
