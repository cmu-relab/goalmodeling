"""
Description: Aggregate speaker turns from a transcript
Authors: breaux@cmu.edu, ateeq@cmu.edu


9-2-2024: minor tweaks and added argparse; AS
"""

import argparse
import csv
import re


class Processor:
    def __init__(self):
        self.data = []
        self.text = None

    def process(self, text):
        self.text = text

        # setup pattern for parsing speaker turns
        pattern = re.compile(r'\s+(\d+)\n\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}\n((.+?):\s(.+?)\n)+')

        # parse instances of pattern, skipping header 'WEBVTT'
        segment0 = 0
        for match in re.finditer(pattern, text[7:]):
            # check for segmentation continuity
            segment1 = int(match.group(1))
            if segment1 != segment0 + 1:
                print('Missing segment between %i and %i' % (segment0, segment1))

            # parse each speaker turn
            for i in range(3, len(match.groups()), 3):
                role = match.group(i)
                text = match.group(i + 1)
                if len(self.data) > 0 and self.data[-1][0] == role:
                    self.data[-1][1] = self.data[-1][1].strip() + ' ' + text
                else:
                    self.data.append([role, text])

            segment0 = segment1

    def reassign_roles(self):
        t_count = {}
        for i, (role, text) in enumerate(self.data):
            if role not in t_count:
                t_count[role] = 0
            t_count[role] += len(text)

        roles = sorted(list(t_count.keys()), key=lambda x: t_count[x], reverse=True)
        new_roles = {
            roles[0]: 'Stakeholder',
            roles[1]: 'Interviewer'
        }
        for i in range(2, len(roles)):
            new_roles[roles[i]] = 'Other ' + str(i - 1)
        for i in range(len(self.data)):
            self.data[i][0] = new_roles[self.data[i][0]]


def main():
    parser = argparse.ArgumentParser(
        prog="aggregator",
        description="Aggregate speaker turns in a transcript",
        epilog="For example, python3 aggregator.py --transcript transcript.txt --output aggregated.csv"
    )

    parser.add_argument('--transcript', type=str, help='Path to transcript file', required=True)
    parser.add_argument('--output', type=str, help='Path to output file', required=True)

    args = parser.parse_args()

    processor = Processor()

    text = open(args.transcript, 'r', encoding='utf-8').read()
    processor.process(text)
    processor.reassign_roles()

    with open(args.output, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Turn', 'Speaker', 'Text'])
        for i, [speaker, speech] in enumerate(processor.data):
            writer.writerow([str(i), speaker, speech])


if __name__ == "__main__":
    main()
