# gc_peasy
Galactic center pulsar search pipeline using 
[peasoup](https://github.com/ewanbarr/peasoup) 
for periodicity searching, 
[PulsarX](https://github.com/ypmen/PulsarX) 
for RFI mitigation and candidate folding, and 
[TransientX](https://github.com/ypmen/TransientX) 
for single pulse searching.

## Overview 
To run the pipeline, make the desired changes to the 
parameter file (`gcpsr_params.py`) and run the search 
script (`gcpsr_search.py`), indicating the top of the 
(temporary) work directory:

```
python gcpsr_search.py /path/to/top/of/workdir
```

This is designed to be run on a remote cluster node, 
but doesn't have to be.

## Expected Data Structure
The expected data structure is as follows.  We will look
for our raw data in the `raw_dir` directory.  This is the 
data files we will run `filtool` on to produce a cleaned 
filterbank file.  The work directory (where all the procesing 
happens) is specified when running the search code.  This is 
done so that we can potentially give the local space on a 
compute node.  Finally, the results of the search will be 
copied back to `results_dir`.

For our Galactic center search we specifically will have a 
bunch of beams with names like `cfbfXXXXX`.  So we will 
specify a beam name and look for the raw data in:

```
raw_dir/cfbfXXXXX/
```

and put the results in 

```
results_dir/cfbfXXXXX/
```

This means that the `raw_dir` and `results_dir` directories 
given in the parameter file will be the top directories, under 
which are the various beam directories.  We set these in 
the parameter file as:

```
raw_dir     = "/hercules/results/rwharton/mmgps_gc/raw"
results_dir = "/hercules/results/rwharton/mmgps_gc/search"
beamname = "cfbf00088"
```

## Software
The pipeline requires [peasoup](https://github.com/ewanbarr/peasoup), 
[PulsarX](https://github.com/ypmen/PulsarX), and 
[TransientX](https://github.com/ypmen/TransientX). Instead of 
installing them proper, we opt instead to utilize them through 
singularity containers.  The location of the relevant singularity 
files is specified in the parameter file:

```
# Singularity files
sing_dir    = "/hercules/results/rwharton/singularity_images"
peasoup_sif = "%s/peasoup_keplerian.sif" %sing_dir
psrX_sif    = "%s/pulsarx_latest.sif" %sing_dir
```

while this is done entirely out of laziness, it has the side 
benefit of ensuring repeatability (so long as you use the same 
singularity files).

## Processing Steps
There are four main processing steps the pipeline can do. 
You can decide which to do in the parameter file by setting 
the following to 1 (do that step) or 0 (do not do that step).

```
# Processing steps to do
do_filtool    = 1      # Run filtool
do_peasoup    = 1      # Run PEASOUP search
do_fold       = 1      # Fold data
do_sp         = 1      # Single Pulse Search with TransientX
```

Currently, we are not keeping the cleaned filterbank file 
after processing, so you generally will have to do the 
`do_filtool` step any time you need the filterbank file 
for subsequent steps.  This can be changed later if desired.


## Setting Options for each Task
This is currently the ugliest part of the pipeline and 
something that we will hopefully change soon.  But for 
now, the way you specify the parameters of a given step 
is to provide the relevant command line arguments as a 
string. For example:

```
# Filtool
ftool_opts = '-t 4 -z kadaneF 4 8 zdot'

# Peasoup
psoup_opts = '-m 7.0 -t 1 --acc_start -100 --acc_end 100 --ram_limit_gb 20.0 --dm_start 500 --dm_end 3000 -n 8'

# TransientX
tX_opts = "-v -t 12 --zapthre 3.0 --fd 1 --overlap 0.1 --dms 500 --ddm 10 --ndm 300 --thre 7 --maxw 0.1 --snrloss 0.1 -l 2.0 --drop -z kadaneF 8 4 zdot"

# TransientX (replot)
replot_opts = "-v -t 6 --zapthre 3.0 --td 1 --fd 1 --dmcutoff 3 --widthcutoff 0.1 --snrcutoff 7 --snrloss 0.1 --zap --zdot --kadane 8 4 7 --clean"
``` 

In the future these will be passed as JSON files.


## Results
If you run everything, you will get the following in `results_dir/cfbfXXXXX`:

* `cand_plots`: `PulsarX` plots of the `peasoup` candidates 
* `sp_plots`: Single pulse plots found with `TransientX`.
    * `sp_plots/all`: All the plots of candidates 
    * `sp_plots/sifted`: Candidates left after sifting with `replot_fil`
* `overview.xml`: Candidate list produced by `peasoup`
* `cfbfXXXXX_YYYYMMDDTHHMMSS.log`: Timing log file produced after each run.

The timing log gives the breakdown of how long each task took:

```
****************************************************
                  TIME SUMMARY
****************************************************

Start Time: 2025-08-12T10:27:30
Stop Time:  2025-08-12T11:30:00

Program:                         Running Time (min):
--------                         -----------------
filtool                          15.07
peasoup                          13.90
fold                             15.95
single pulse                     16.57

Total Runtime = 62.50 min
```
