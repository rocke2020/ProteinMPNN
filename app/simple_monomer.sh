folder_with_pdbs="/home/qcdong/codes/RFdiffusion/test_outputs/"

output_dir="outputs2/monomers_outputs"
if [ ! -d $output_dir ]
then
    mkdir -p $output_dir
fi

path_for_parsed_chains=$output_dir"/parsed_pdbs.jsonl"

python helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains

file=app/protein_mpnn_run.log
python protein_mpnn_run.py \
        --jsonl_path $path_for_parsed_chains \
        --out_folder $output_dir \
        --num_seq_per_target 2 \
        --sampling_temp "0.1" \
        --seed 37 \
        --batch_size 1 \
        2>&1  </dev/null | tee $file.log

python app/replace_aa_with_generated.py \
    --input_path=$folder_with_pdbs \
    --output_path=$output_dir
