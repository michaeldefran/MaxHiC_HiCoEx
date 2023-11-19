"""
Author: Michael de Francesco
Date created: 11/08/2023

Description: This script is used preprocess the output from MaxHiC so that
it can be loaded into HiCoEx. 
"""
import os
import argparse
import math
import scipy.sparse as sps
import pandas as pd
import time

def main(args):
    # Load cis_interactions.txt
    print('Loading interactions file.')
    cisint = pd.read_csv(args.cisint_input, usecols=['bin1ID', 'bin2ID', 'neg_ln_p_val', 'observed_interactions'], delimiter='\t')
    cisint[['bin1ID', 'bin2ID']] = cisint[['bin1ID', 'bin2ID']].astype(int)

    # Map the chromosome number to the binID
    print('Mapping bins to chromosomes using .bed annotations file.')
    beddf = pd.read_csv(args.bed_input, delimiter='\t', header=None, usecols=[0, 2, 3], names=['Chromosome', 'End', 'binID'])
    cisint = pd.merge(cisint, beddf, left_on='bin1ID', right_on='binID', how='left')
    cisint.rename(columns={'Chromosome': 'bin1Chr'}, inplace=True)
    cisint.drop(columns='binID', inplace=True)
    cisint = pd.merge(cisint, beddf, left_on='bin2ID', right_on='binID', how='left')
    cisint.rename(columns={'Chromosome': 'bin2Chr'}, inplace=True)
    cisint.drop(columns='binID', inplace=True)

    # Take significant Hi-C contacts from cis_interactions.txt
    print('Taking significant Hi-C contacts.')
    signifcisint = cisint[cisint['neg_ln_p_val'] >= -1*math.log(args.pval)]
    dataset_path = f'../../data/{args.dataset}/hic_raw'
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path, exist_ok=True)

    # Split by chromosome to get 22 respective matrices
    chromosomes = range(1, 23) if args.chromosomes is None else args.chromosomes
    for chr in chromosomes:
        print(f'Creating matrix for chromosome {chr}.')
        dfchr = signifcisint[(signifcisint['bin1Chr'] == 'chr'+str(chr)) &
                             (signifcisint['bin2Chr'] == 'chr'+str(chr))]

        dfchr[['End_x', 'End_y']] = dfchr[['End_x', 'End_y']] // args.resolution

        # Remove columns not needed for COO format
        dfchr = dfchr.drop(columns=['bin1Chr', 'bin2Chr', 'neg_ln_p_val', 'bin1ID', 'bin2ID'])

        # Save the contact maps into sparse contact matrices
        print('Saving matrix.')
        bin1 = dfchr['End_x'].values
        bin2 = dfchr['End_y'].values
        data = dfchr['observed_interactions'].values
        chrlength = len(beddf[beddf['Chromosome'] == 'chr'+str(chr)])
        contact_matrix_sparse = sps.coo_matrix((data,(bin1,bin2)), shape=(chrlength, chrlength)).tocsr()
        sps.save_npz(dataset_path + f'/hic_raw_{chr}_{chr}_{args.resolution}.npz',
                    contact_matrix_sparse)

    print('Hi-C data saved in sparse format in', dataset_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument('--resolution', type=int, required=True,
                        help='Resolution of the Hi-C data.')
    parser.add_argument('--pval', type=float, default=0.05,
                        help='The p-value threshold used in MaxHiC.')
    parser.add_argument('--cisint_input', type=str, required=True,
                        help='The path of the cis_interactions.txt file')
    parser.add_argument('--bed_input', type=str, required=True,
                        help='The path of the bed annotations file')
    parser.add_argument('--chromosomes', nargs='*', default=None,
                        help='List of chromosomes for which to process Hi-C data. If empty all the autosomes data will be processed.')
    args = parser.parse_args()
    
    start_time = time.time()
    main(args)
    print("Preprocessing Hi-C data took %s seconds" % (time.time() - start_time))