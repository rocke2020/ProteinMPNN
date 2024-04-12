import argparse
import json
import math
import os
import random
import re
import shutil
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from icecream import ic
from loguru import logger
from tqdm import tqdm

sys.path.append(os.path.abspath("."))


ic.configureOutput(includeContext=True, argToStringFunction=str)
ic.lineWrapWidth = 120
score_pat = re.compile(r"\sscore=(\d+\.\d+)")
global_score_pat = re.compile(r"\sglobal_score=(\d+\.\d+)")
designed_chains_pat = re.compile(r"designed_chains=\['(.*)'\]")
alpha_1 = list("ARNDCQEGHILKMFPSTWYV-")
alpha_3 = [
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLN",
    "GLU",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
    "GAP",
]

aa_1_3 = {a: b for a, b in zip(alpha_1, alpha_3)}


@dataclass
class GeneratedSeq(object):
    """
    docstring
    """

    seq: str
    score: float
    global_score: float
    designed_chain: str = "A"


def main(args):
    new_pdb_dir = Path(args.output_path) / "new_pdbs"
    new_pdb_dir.mkdir(parents=True, exist_ok=True)
    for orig_pdb_file in Path(args.input_path).glob("*.pdb"):
        generated_seqs_file = (
            Path(args.output_path) / "seqs" / f"{orig_pdb_file.stem}.fa"
        )
        if not generated_seqs_file.exists():
            logger.warning(f"{generated_seqs_file} does not exist")
            continue
        generated_seqs = []
        with open(generated_seqs_file, encoding="utf-8") as f:
            is_generated_seq = False
            for i, line in enumerate(f):
                if i == 0:
                    if got:= designed_chains_pat.search(line):
                        designed_chain = got.group(1)
                        if args.verbose:
                            logger.info(f"{designed_chain = }")
                    else:
                        raise ValueError(
                            f"No designed_chains found in the first line: {line}"
                        )
                elif line.startswith(">T="):
                    is_generated_seq = True
                    if got := score_pat.search(line):
                        score = float(got.group(1))
                    else:
                        logger.warning(f"No score found in {line}")
                        score = 0.0
                    if got := global_score_pat.search(line):
                        global_score = float(got.group(1))
                    else:
                        logger.warning(f"No global_score found in {line}")
                        global_score = 0.0
                    continue
                if is_generated_seq:
                    generated_seqs.append(
                        GeneratedSeq(line.strip(), score, global_score, designed_chain)
                    )
                    is_generated_seq = False
        if not generated_seqs:
            logger.warning(f"No generated seqs found in {generated_seqs_file}")
            continue
        # logger.info(f"{generated_seqs = }")

        with open(orig_pdb_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for index, generated_seq in enumerate(generated_seqs):
            new_lines = []
            for line in lines:
                items = line.split()
                chain = items[4]
                if chain == designed_chain:
                    aa_ind = items[5]
                    aa = generated_seq.seq[int(aa_ind) - 1]
                    _line = line.replace("GLY", aa_1_3[aa])
                else:
                    _line = line
                new_lines.append(_line)
            new_pdb_file = (
                new_pdb_dir
                / f"{orig_pdb_file.stem}_{index}_score{generated_seq.score:.2f}.pdb"
            )
            with open(new_pdb_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=2, type=int)
    parser.add_argument("--verbose", default=0, type=int)
    parser.add_argument(
        "--input_path", type=str, help="Path to a folder with pdb files"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        help="Path to have sub dir 'seqs' of generated seqs in .fa files",
    )
    _args = parser.parse_args()
    random.seed(_args.seed)
    main(_args)
    logger.info("end")
