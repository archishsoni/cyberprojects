# cyberprojects
cybersecurity inspired projects

## PhishCatcher

`PhishCatcher` is a simple command line tool that analyzes raw email files for potential phishing indicators.

### Usage

```bash
python phishcatcher/phishcatcher.py path/to/email.eml
```

Optional arguments:

- `-o OUTPUT` – export the report to a text file.
- `--json` – export the report in JSON format.

### Phishing keywords

The tool loads keywords from `phishcatcher/phishing_keywords.txt`. Modify this file to adapt the keyword list.

