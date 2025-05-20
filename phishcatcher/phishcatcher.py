#!/usr/bin/env python3
"""PhishCatcher CLI tool.
Analyzes raw email files to detect phishing attempts.
"""
import argparse
import re
import sys
import json
from urllib.parse import urlparse
from email import policy
from email.parser import BytesParser


SHORTENER_DOMAINS = {
    'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
    'buff.ly', 'adf.ly', 'bit.do', 'cutt.ly', 'is.gd'
}

IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?$")
URL_REGEX = re.compile(r"https?://[^\s'\"]+")
ANCHOR_REGEX = re.compile(r"<a\s+href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.IGNORECASE)


class PhishCatcher:
    def __init__(self, keyword_file: str):
        with open(keyword_file, 'r', encoding='utf-8') as f:
            self.keywords = [line.strip().lower() for line in f if line.strip()]

    def parse_email(self, path: str):
        with open(path, 'rb') as f:
            data = f.read()
        msg = BytesParser(policy=policy.default).parsebytes(data)
        body = self._get_body(msg)
        headers = {
            'From': msg.get('From', ''),
            'Reply-To': msg.get('Reply-To', ''),
            'Subject': msg.get('Subject', ''),
            'Date': msg.get('Date', '')
        }
        return headers, body

    def _get_body(self, msg):
        if msg.is_multipart():
            parts = [part.get_content() for part in msg.walk()
                     if part.get_content_type() == 'text/plain']
            return '\n'.join(parts)
        return msg.get_content()

    def analyze(self, headers, body):
        report = {
            'headers': headers,
            'suspicious_keywords': [],
            'urls': [],
            'flags': []
        }
        score = 0

        # Domain mismatch check
        from_domain = self._extract_domain(headers.get('From'))
        reply_domain = self._extract_domain(headers.get('Reply-To'))
        if from_domain and reply_domain and from_domain != reply_domain:
            report['flags'].append('From and Reply-To domains differ')
            score += 30

        # Keyword search
        body_lower = body.lower()
        for kw in self.keywords:
            if kw in body_lower:
                report['suspicious_keywords'].append(kw)
                score += 5

        # URL checks
        urls = URL_REGEX.findall(body)
        for url in urls:
            url_info = {'url': url, 'issues': []}
            parsed = urlparse(url)
            domain = parsed.netloc
            # IP address check
            if IP_REGEX.match(domain):
                url_info['issues'].append('Uses IP address')
                score += 20
            # URL shortener check
            if domain.lower() in SHORTENER_DOMAINS:
                url_info['issues'].append('URL shortener')
                score += 15
            report['urls'].append(url_info)

        # Anchor text mismatch check
        for href, text in ANCHOR_REGEX.findall(body):
            parsed = urlparse(href)
            if text.strip() and text.strip() != href and parsed.netloc not in text:
                report['flags'].append(f'Anchor text mismatch: "{text}" -> {href}')
                score += 25

        report['score'] = min(100, score)
        return report

    @staticmethod
    def _extract_domain(address):
        match = re.search(r"@([^>]+)", address or '')
        if match:
            return match.group(1).lower()
        return None


def print_report(report):
    headers = report['headers']
    print("PhishCatcher Report")
    print("-" * 20)
    for key in ['From', 'Reply-To', 'Subject', 'Date']:
        print(f"{key}: {headers.get(key, '')}")
    print()
    if report['flags']:
        print("Flags:")
        for flag in report['flags']:
            print(f" - {flag}")
    else:
        print("Flags: none")
    print()
    if report['suspicious_keywords']:
        print("Suspicious Keywords:")
        for kw in report['suspicious_keywords']:
            print(f" - {kw}")
    else:
        print("Suspicious Keywords: none")
    print()
    if report['urls']:
        print("URLs:")
        for item in report['urls']:
            line = f" - {item['url']}"
            if item['issues']:
                line += " (" + ', '.join(item['issues']) + ")"
            print(line)
    else:
        print("URLs: none")
    print()
    print(f"Phishing Likelihood Score: {report['score']}%")


def main():
    parser = argparse.ArgumentParser(description='Analyze emails for phishing indicators')
    parser.add_argument('input', help='Path to raw email file (.txt or .eml)')
    parser.add_argument('-o', '--output', help='Optional path to output report file')
    parser.add_argument('--json', action='store_true', help='Export report in JSON format')
    args = parser.parse_args()

    catcher = PhishCatcher(keyword_file=str(__file__).replace('phishcatcher.py', 'phishing_keywords.txt'))
    headers, body = catcher.parse_email(args.input)
    report = catcher.analyze(headers, body)

    if args.output:
        if args.json:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                print_report(report)
                sys.stdout = original_stdout

    print_report(report)


if __name__ == '__main__':
    main()
