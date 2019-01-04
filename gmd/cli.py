import os
import sys
import logging

from .command import Command, Option


def main():
    logging.basicConfig(filename='log', filemode='w', level=logging.DEBUG)
    task = Command(
        options=[
            Option('file', 'f', 'Alternative config file', many=True),
            Option('help', 'h', 'Get help', typ='B'),
        ],
        mutexopts=[
            (('help',), ('file',))
        ]
    )

    if os.environ.get('_GMD_COMPLETE'):
        words = sys.argv
        current = int(os.environ.get('CURRENT'))
        sofar = words[2:current]
        print(task.complete(sofar))
        sys.exit(0)

    for a in sys.argv:
        print(a)
