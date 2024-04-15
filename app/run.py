import argparse
import logging
import os
import random
import sys
from pathlib import Path

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    datefmt="%y-%m-%d %H:%M",
    format="%(asctime)s %(filename)s %(lineno)d: %(message)s",
)

sys.path.append(os.path.abspath("."))
from app.replace_aa_with_generated import main as replace_aa_with_generated
from helper_scripts.assign_fixed_chains import main as assign_fixed_chains
from helper_scripts.parse_multiple_chains import main as parse_multiple_chains
from protein_mpnn_run import main as protein_mpnn_run


def main(args):
    output_root = Path(args.output_root)
    output_root.mkdir(exist_ok=True, parents=True)
    path_for_parsed_chains = output_root / "parsed_pdbs.jsonl"
    args.input_path = args.folder_with_pdbs
    args.output_path = path_for_parsed_chains
    logger.info("parse_multiple_chains")
    parse_multiple_chains(args)

    path_for_assigned_chains = output_root / "assigned_pdbs.jsonl"
    args.input_path = path_for_parsed_chains
    args.output_path = path_for_assigned_chains
    logger.info("assign_fixed_chains")
    assign_fixed_chains(args)

    args.jsonl_path = path_for_parsed_chains
    args.chain_id_jsonl = path_for_assigned_chains
    args.out_folder = args.output_root
    logger.info("protein_mpnn_run")
    protein_mpnn_run(args)

    args.input_path = args.folder_with_pdbs
    args.output_path = args.output_root
    logger.info("replace_aa_with_generated")
    replace_aa_with_generated(args)
    logger.info("end")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_with_pdbs", type=str, help="input dir")
    parser.add_argument("--output_root", type=str, help="")
    parser.add_argument("--chain_list", type=str, default="A", help="chains_to_design")
    # replace_aa_with_generated arguments
    parser.add_argument("--verbose", type=int, default="0", help="")
    # ProteinMPNN arguments
    parser.add_argument(
        "--suppress_print", type=int, default=0, help="0 for False, 1 for True"
    )
    parser.add_argument(
        "--ca_only",
        action="store_true",
        default=False,
        help="Parse CA-only structures and use CA-only models (default: false)",
    )
    parser.add_argument(
        "--path_to_model_weights",
        type=str,
        default="",
        help="Path to model weights folder;",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="v_48_020",
        help="ProteinMPNN model name: v_48_002, v_48_010, v_48_020, v_48_030; v_48_010=version with 48 edges 0.10A noise",
    )
    parser.add_argument(
        "--use_soluble_model",
        action="store_true",
        default=False,
        help="Flag to load ProteinMPNN weights trained on soluble proteins only.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="If set to 0 then a random seed will be picked;",
    )
    parser.add_argument(
        "--save_score",
        type=int,
        default=0,
        help="0 for False, 1 for True; save score=-log_prob to npy files",
    )
    parser.add_argument(
        "--save_probs",
        type=int,
        default=0,
        help="0 for False, 1 for True; save MPNN predicted probabilites per position",
    )
    parser.add_argument(
        "--score_only",
        type=int,
        default=0,
        help="0 for False, 1 for True; score input backbone-sequence pairs",
    )
    parser.add_argument(
        "--path_to_fasta",
        type=str,
        default="",
        help="score provided input sequence in a fasta format; e.g. GGGGGG/PPPPS/WWW for chains A, B, C sorted alphabetically and separated by /",
    )
    parser.add_argument(
        "--conditional_probs_only",
        type=int,
        default=0,
        help="0 for False, 1 for True; output conditional probabilities p(s_i given the rest of the sequence and backbone)",
    )
    parser.add_argument(
        "--conditional_probs_only_backbone",
        type=int,
        default=0,
        help="0 for False, 1 for True; if true output conditional probabilities p(s_i given backbone)",
    )
    parser.add_argument(
        "--unconditional_probs_only",
        type=int,
        default=0,
        help="0 for False, 1 for True; output unconditional probabilities p(s_i given backbone) in one forward pass",
    )
    parser.add_argument(
        "--backbone_noise",
        type=float,
        default=0.00,
        help="Standard deviation of Gaussian noise to add to backbone atoms",
    )
    parser.add_argument(
        "--num_seq_per_target",
        type=int,
        default=2,
        help="Number of sequences to generate per target",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size; can set higher for titan, quadro GPUs, reduce this if running out of GPU memory",
    )
    parser.add_argument(
        "--max_length", type=int, default=200000, help="Max sequence length"
    )
    parser.add_argument(
        "--sampling_temp",
        type=str,
        default="0.1",
        help="A string of temperatures, 0.2 0.25 0.5. Sampling temperature for amino acids. Suggested values 0.1, 0.15, 0.2, 0.25, 0.3. Higher values will lead to more diversity.",
    )
    parser.add_argument(
        "--out_folder",
        type=str,
        help="Path to a folder to output sequences, e.g. /home/out/",
    )
    parser.add_argument(
        "--pdb_path", type=str, default="", help="Path to a single PDB to be designed"
    )
    parser.add_argument(
        "--pdb_path_chains",
        type=str,
        default="",
        help="Define which chains need to be designed for a single PDB ",
    )
    parser.add_argument(
        "--jsonl_path", type=str, help="Path to a folder with parsed pdb into jsonl"
    )
    parser.add_argument(
        "--chain_id_jsonl",
        type=str,
        default="",
        help="Path to a dictionary specifying which chains need to be designed and which ones are fixed, if not specied all chains will be designed.",
    )
    parser.add_argument(
        "--fixed_positions_jsonl",
        type=str,
        default="",
        help="Path to a dictionary with fixed positions",
    )
    parser.add_argument(
        "--omit_AAs",
        type=list,
        default="X",
        help="Specify which amino acids should be omitted in the generated sequence, e.g. 'AC' would omit alanine and cystine.",
    )
    parser.add_argument(
        "--bias_AA_jsonl",
        type=str,
        default="",
        help="Path to a dictionary which specifies AA composion bias if neededi, e.g. {A: -1.1, F: 0.7} would make A less likely and F more likely.",
    )

    parser.add_argument(
        "--bias_by_res_jsonl",
        default="",
        help="Path to dictionary with per position bias.",
    )
    parser.add_argument(
        "--omit_AA_jsonl",
        type=str,
        default="",
        help="Path to a dictionary which specifies which amino acids need to be omited from design at specific chain indices",
    )
    parser.add_argument(
        "--pssm_jsonl", type=str, default="", help="Path to a dictionary with pssm"
    )
    parser.add_argument(
        "--pssm_multi",
        type=float,
        default=0.0,
        help="A value between [0.0, 1.0], 0.0 means do not use pssm, 1.0 ignore MPNN predictions",
    )
    parser.add_argument(
        "--pssm_threshold",
        type=float,
        default=0.0,
        help="A value between -inf + inf to restric per position AAs",
    )
    parser.add_argument(
        "--pssm_log_odds_flag", type=int, default=0, help="0 for False, 1 for True"
    )
    parser.add_argument(
        "--pssm_bias_flag", type=int, default=0, help="0 for False, 1 for True"
    )

    parser.add_argument(
        "--tied_positions_jsonl",
        type=str,
        default="",
        help="Path to a dictionary with tied positions",
    )

    _args = parser.parse_args()
    random.seed(_args.seed)
    main(_args)
