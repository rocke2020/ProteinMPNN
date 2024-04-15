folder_with_pdbs="/home/qcdong/codes/peptide-deploy/outputs/monomer_test"

# output_root="outputs2/monomers_outputs"
output_root="outputs2/binder_outputs2"
if [ ! -d $output_root ]
then
    mkdir -p $output_root
fi

path_for_parsed_chains=$output_root"/parsed_pdbs.jsonl"
path_for_assigned_chains=$output_root"/assigned_pdbs.jsonl"
chains_to_design="A"

python helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains

python helper_scripts/assign_fixed_chains.py --input_path=$path_for_parsed_chains --output_path=$path_for_assigned_chains --chain_list "$chains_to_design"

file=app/protein_mpnn_run.log
python protein_mpnn_run.py \
        --jsonl_path $path_for_parsed_chains \
        --chain_id_jsonl $path_for_assigned_chains \
        --out_folder $output_root \
        --num_seq_per_target 2 \
        --sampling_temp "0.1" \
        --seed 37 \
        --batch_size 1 \
        2>&1  </dev/null | tee $file.log

python app/replace_aa_with_generated.py \
    --input_path=$folder_with_pdbs \
    --output_path=$output_root
