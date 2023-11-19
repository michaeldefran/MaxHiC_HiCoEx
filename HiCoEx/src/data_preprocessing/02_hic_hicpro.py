"""
Author: Michael de Francesco
Date created: 30/08/2023

Description: This script is used preprocess Hi-C data in HiC-Pro format so that
it is compatible with the HiCoEx pipeline.

IMPORTANT:
Ensure the ICED contact maps are used from HiC-Pro, not the raw reads.
"""
import os
import argparse
import scipy.sparse as sps
import pandas as pd
import time

def main(args):
    # Loading .matrix file.
    print('Loading interactions file.')
    intdf = pd.read_csv(args.matint_input, names=['bin1ID', 'bin2ID', 'read_count'], delimiter='\t')
    intdf[['bin1ID', 'bin2ID']] = intdf[['bin1ID', 'bin2ID']].astype(int)

    # Map the chromosome number to the binID
    print('Mapping bins to chromosomes using .bed annotations file.')
    beddf = pd.read_csv(args.bed_input, delimiter='\t', header=None, usecols=[0, 2, 3], names=['Chromosome', 'End', 'binID'])
    intdf = pd.merge(intdf, beddf, left_on='bin1ID', right_on='binID', how='left')
    intdf.rename(columns={'Chromosome': 'bin1Chr'}, inplace=True)
    intdf.drop(columns='binID', inplace=True)
    intdf = pd.merge(intdf, beddf, left_on='bin2ID', right_on='binID', how='left')
    intdf.rename(columns={'Chromosome': 'bin2Chr'}, inplace=True)
    intdf.drop(columns='binID', inplace=True)
 
    dataset_path = f'../../data/{args.dataset}/hic_raw'
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path, exist_ok=True)

    # Split by chromosome to get 22 respective matrices
    chromosomes = range(1, 23) if args.chromosomes is None else args.chromosomes
    for chr in chromosomes:
        print(f'Creating matrix for chromosome {chr}.')
        dfchr = intdf[(intdf['bin1Chr'] == 'chr'+str(chr)) &
                             (intdf['bin2Chr'] == 'chr'+str(chr))]

        dfchr.loc[:, ['End_x', 'End_y']] = dfchr[['End_x', 'End_y']] // args.resolution

        # Remove columns not needed for COO format
        dfchr = dfchr.drop(columns=['bin1Chr', 'bin2Chr', 'bin1ID', 'bin2ID'])

        # Save the contact maps into sparse contact matrices
        print('Saving matrix.')
        bin1 = dfchr['End_x'].values
        bin2 = dfchr['End_y'].values
        data = dfchr['read_count'].values
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
    parser.add_argument('--matint_input', type=str, required=True,
                        help='The path of the matrix interactions file')
    parser.add_argument('--bed_input', type=str, required=True,
                        help='The path of the bed annotations file')
    parser.add_argument('--chromosomes', nargs='*', default=None,
                        help='List of chromosomes for which to process Hi-C data. If empty all the autosomes data will be processed.')
    args = parser.parse_args()
    
    start_time = time.time()
    main(args)
    print("Preprocessing Hi-C data took %s seconds" % (time.time() - start_time))