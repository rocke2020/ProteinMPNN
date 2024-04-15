# 
file=app/run.py
python $file \
    --folder_with_pdbs "/home/qcdong/codes/peptide-deploy/outputs/binder_insulin" \
    --output_root "outputs2/ProteinMPNN_outputs" \
    --chain_list "A" \
    --num_seq_per_target 2 \
    --batch_size 1 \
    --seed 0 \
    2>&1  </dev/null | tee $file.log