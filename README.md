# MaxHiC_HiCoEx
This repository contains both MaxHiC and HiCoEx tools. Along with the updated functionality of HiCoEx to integrate MaxHiC output data and the ability to use Hi-C Pro format within HiCoEx. 

## Running the pipeline
Use the `run_maxhicmuscle.sh` file as a guide to running both tools in conjunction. Note when using MaxHiC output, the Hi-C percentile cutoff should be set to 0.0 when using `04_chromatin_network.py` so all contacts are considered significant.

Refer to (MaxHiC Repository)[https://github.com/bcb-sut/MaxHiC] for help with MaxHiC.
Instructions for HiCoEx can be found in HiCoEx/README.md.
