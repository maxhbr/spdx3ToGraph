import re
import os
import sys
import csv
import json
import logging
import hashlib
import uuid
from datetime import datetime, timezone
import subprocess
import multiprocessing
from collections import defaultdict
import argparse
from pathlib import Path

from . import spdx30 as spdx


def main():
    parser = argparse.ArgumentParser(
                    prog='spdx3_to_graph',
                    description='create a visualization of SPDX 3.0 documents',)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('spdx', type=Path)


    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"args: {args}")
    logging.info(f"Processing {args.spdx}")

    objectset = spdx.SHACLObjectSet()
    with args.spdx.open("r") as f:
        d = spdx.JSONLDDeserializer()
        d.read(f, objectset)

    if args.verbose:
        spdx.print_tree(objectset.objects)
