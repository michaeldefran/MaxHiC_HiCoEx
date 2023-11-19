DATASET=maxhicmuscle0.01 
DATA_ROOT=/media/rokny/DATA2/michaeldefran/HiCoEx/data
MAXHIC_ROOT=/media/rokny/DATA2/michaeldefran/MaxHiC/MaxHic-master
BASE_DIR=/media/rokny/DATA2/michaeldefran/Muscle_HiC/5000
SAVE_DIR=/media/rokny/DATA2/michaeldefran/Muscle_HiC/maxhic5000output
EXPRESSION_PATH=/media/rokny/DATA2/michaeldefran/HiCoEx/data/${DATASET}/muscle-skeletal.csv
CISINTINPUT=${SAVE_DIR}/cis_interactions.txt
BEDINPUT=/media/rokny/DATA2/michaeldefran/Muscle_HiC/5000/Dixon_2M_5000_abs.bed
RESOLUTION=5000
COEXP_PERCENTILE=90.0
HIC_PERCENTILE=0.0 # Ensure Hi-C percentile is set to 0.0 when using MaxHiC contacts so all contacts are considered significant.

cd ../
python $MAXHIC_ROOT/Main.py $BASE_DIR $SAVE_DIR
cd HiCoEx

# Make sure run_split_tissues.sh is executed first if using GTEx Expression
cd ./src/data_preprocessing
python 01_gene_expression.py --input $EXPRESSION_PATH --dataset $DATASET
python 02_hic_maxhic.py --dataset $DATASET --cisint_input $CISINTINPUT --bed_input $BEDINPUT --resolution $RESOLUTION --pval 0.01

cd ../network_construction
python 01_compute_coexpression.py --data-root $DATA_ROOT --dataset $DATASET --save-plot --save-coexp
python 02_coexpression_network.py --data-root $DATA_ROOT --dataset $DATASET --perc-intra $COEXP_PERCENTILE --save-matrix --save-plot
python 03_hic_gene_selection.py --data-root $DATA_ROOT --dataset $DATASET --type observed --resolution $RESOLUTION --save-matrix --save-plot
python 04_chromatin_network.py --data-root $DATA_ROOT --dataset $DATASET --type observed --resolution $RESOLUTION --type-inter observed --resolution-inter $RESOLUTION --perc-intra $HIC_PERCENTILE --save-matrix --save-plot

cd ../link_prediction
GPU_ID=0
for  i in `seq 1 22`
do
  python 01_link_prediction_chromosome.py --data-root $DATA_ROOT --dataset $DATASET --chr-src $i --chr-tgt $i --method GNN_HiCoEx --chromatin-network-name observed_${i}_${i}_${RESOLUTION}_${HIC_PERCENTILE} --aggregators hadamard --coexp-thr $COEXP_PERCENTILE --epoches 100 --batch-size 64 --init_lr 1e-3 --weight-decay 5e-4 --classifier 'mlp' --n-layers 1 --gpu --gpu-id $GPU_ID --training --times 0 --seed 42
done

GPU_ID=0
python 02_link_prediction_intra.py --data-root $DATA_ROOT --dataset $DATASET --method GNN_HiCoEx_pyg --type observed  --aggregators hadamard --coexp-thr $COEXP_PERCENTILE --bin-size $RESOLUTION --hic-threshold $HIC_PERCENTILE --epoches 100 --batch-size 128 --init_lr 1e-3 --weight-decay 5e-4 --classifier 'mlp' --n-layers 1 --epoches 25 --gpu --gpu-id $GPU_ID --training --times 0 --seed 42
python 02_link_prediction_intra.py --data-root $DATA_ROOT --dataset $DATASET --method GNN_HiCoEx_pyg --type observed  --aggregators hadamard --coexp-thr $COEXP_PERCENTILE --bin-size $RESOLUTION --hic-threshold $HIC_PERCENTILE --epoches 100 --batch-size 128 --init_lr 1e-3 --weight-decay 5e-4 --classifier 'mlp' --n-layers 1 --epoches 25 --gpu --gpu-id $GPU_ID --force --load-ckpt --test --times 0 --seed 42

