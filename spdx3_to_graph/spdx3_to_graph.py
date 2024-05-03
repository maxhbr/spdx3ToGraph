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
import collections.abc
import re

from . import spdx30 as spdx

def escape_string(s):
    # escapes newlines and quotes
    return s.replace("\n", "\\n").replace("\"", "\\\"")

class SPDXPumlGraph():

    def _get_idx(self, _id):
        if _id is None:
            logging.error(f"None id")
            raise ValueError("None id")
        if _id not in self.id_to_idx:
            idx = f"o{len(self.id_to_idx)}"
            self.id_to_idx[_id] = idx
            self.idx_to_id[idx] = _id
            return idx
        else:
            return self.id_to_idx[_id]

    def _get_idx_of_shaclobject(self, o):
        if o is None:
            raise ValueError("None object")
        _id = o._id
        if o._id is None:
            _id = id(o)
            if _id not in self.id_to_idx:
                logging.warn(f"None id for {type(o)}, use {_id}")
        return self._get_idx(_id)

    def _get_idx_of_str(self, o):
        if o is None:
            raise ValueError("None str")
        if o not in self.id_to_idx:
            idx = hashlib.md5(o.encode()).hexdigest()
            self.id_to_idx[o] = idx
            self.idx_to_id[idx] = o
            return idx
        else:
            return self.id_to_idx[o]


    def _create_node(self, o):
        if isinstance(o, spdx.SHACLObject):
            idx = self._get_idx_of_shaclobject(o)
            if idx in self.inserted:
                return idx
            self.inserted.add(idx)
            self.logging.debug(f"Create node: {o._id} as {idx}: {o}")

            if isinstance(o, spdx.Element) and o.name is not None:
                self.lines_defs.append(f"object \"<b>{o.name}</b>\\n{o.__class__.__name__}\" as {idx}")
            elif o._id is None:
                self.lines_defs.append(f"object \"{o.__class__.__name__}\" as {idx}")
            else:
                self.lines_defs.append(f"object \"{o._id}\\n{o.__class__.__name__}\" as {idx}")

            for pyname, iri, compact in o.property_keys():
                value = o._obj_data[iri]
                if value is None:
                    continue
                if value == []:
                    continue
                if value == {}:
                    continue
                logging.debug(f"  {pyname} has value {value}")
                if isinstance(value, spdx.SHACLObject):
                    logging.debug(f"    {pyname} is of type SHACLObject")
                    other_idx = self._create_node(value)
                    if compact == "from":
                        self.lines.append(f"{other_idx} <-- {idx}::{compact} : {compact}")
                    else:
                        self.lines.append(f"{idx}::{compact} --> {other_idx} : {compact}")
                    continue
                if isinstance(value, list) or isinstance(value, collections.abc.Iterable):
                    logging.debug(f"    {pyname} has list of objects")
                    if isinstance(value[0], spdx.SHACLObject):
                        logging.debug(f"      {pyname} has list of objects")
                        for v in value:
                            other_idx = self._create_node(v)
                            self.lines.append(f"{idx}::{compact} --> {other_idx} : {compact}")
                        continue

                if isinstance(value, str):
                    self.lines.append(f"{idx} : {compact} = \"{escape_string(value)}\"")
                else:
                    self.lines.append(f"{idx} : {compact} = {value}")
        elif isinstance(o, str):
            idx = self._get_idx_of_str(o)
            self.logging.debug(f"Create str node: {idx}")
            self.lines_defs.append(f"object \"{escape_string(o)}\" as {idx}")
        else:
            raise ValueError(f"Unknown type {type(o)}")

        return idx


    def __init__(self, logging, objectset):
        self.logging = logging
        self.inserted = set()
        self.lines_defs = []
        self.lines = []
        self.id_to_idx = {}
        self.idx_to_id = {}

        for o in objectset.foreach():
            self._create_node(o)

    def all_lines(self):
        return ["@startuml"] + self.lines_defs + self.lines + ["@enduml"]

    def print(self):
        for l in self.all_lines():
            print(l)
    def write(self, f):
        for l in self.all_lines():
            f.write(l)
            f.write("\n")

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

    P = SPDXPumlGraph(logging, objectset)
    P.print()
    P.write(open(f"{args.spdx}.puml", "w"))
