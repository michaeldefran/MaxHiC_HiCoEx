import os
import argparse
import pandas as pd
import numpy as np


def main(args):
    reads = pd.read_csv(args.expression_path, delimiter='\t', skiprows=2)
    reads = reads.set_index('Description')

    info = pd.read_csv(args.annotations_path, delimiter='\t')
    # if args.tissues is not None:
    #     tissuse = args.tissues
    # else:
    #     tissues = np.unique(info['SMTSD'])
    tissues = ['Brain - Cortex', 'Brain - Cerebellum', 'Brain - Frontal Cortex (BA9)', 'Brain - Cerebellar Hemisphere', 'Brain - Amygdala', 'Brain - Anterior cingulate cortex (BA24)', 'Brain - Caudate (basal ganglia)', 'Brain - Hippocampus', 'Brain - Hypothalamus', 'Brain - Nucleus accumbens (basal ganglia)', 'Brain - Putamen (basal ganglia)', 'Brain - Spinal cord (cervical c-1)', 'Brain - Substantia nigra', 'Muscle - Skeletal']
    # import ipdb
    # ipdb.set_trace()
    samples_reads_ids = reads.columns
    for tissue in tissues:
        print('Tissue', tissue)
        sample_ids = info[info['SMTSD'] == tissue]['SAMPID']
        sample_ids = np.intersect1d(sample_ids, samples_reads_ids)
        samples_tissue = reads[sample_ids]
        samples_tissue = samples_tissue.rename(columns={'Description': 'sample'})
        samples_tissue = np.log1p(samples_tissue)
        
        filename = tissue.lower().replace(' - ', '-').replace(' ', '_')
        samples_tissue.to_csv(os.path.join(args.output_path, filename+'.csv'), sep='\t', index_label='sample')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--expression-path', type=str, required=True)
    parser.add_argument('--annotations-path', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()

    main(args)

