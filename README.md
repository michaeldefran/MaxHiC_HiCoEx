# MaxHiC_HiCoEx
This repository contains both MaxHiC and HiCoEx tools. Along with the updated functionality of HiCoEx to integrate MaxHiC output data and the ability to use Hi-C Pro format within HiCoEx. 

## Running the pipeline
Use the `run_maxhicmuscle.sh` file as a guide to running both tools in conjunction. Note when using MaxHiC output, the Hi-C percentile cutoff should be set to 0.0 when using `04_chromatin_network.py` so all contacts are considered significant.

Refer to [MaxHiC Repository](https://github.com/bcb-sut/MaxHiC) for help with MaxHiC.
Instructions for HiCoEx can be found in HiCoEx/README.md.

## New HiCoEx files
Details on how to use these scripts can be found by using the `--help` flag.

### `02_hic_hicpro.py`
This script is used in data preprocessing when using Hi-C data in Hi-C Pro format. Important to note that the ICED contacts maps should be used as input, not the raw reads.

### `02_hic_maxhic.py`
This script is used to preprocess the output from MaxHiC so that it can be loaded into HiCoEx.
