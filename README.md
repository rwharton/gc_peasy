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
JSON parameter file (`proc_args.json`) and run the search 
script (`gcpsr_search2.py`), indicating the top of the 
(temporary) work directory and the beam number.

```
python gcpsr_search2.py --work_dir /path/to/top/of/workdir --beam 2 --args_json /path/to/proc_args.json
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
"dirs" :
        {
            "raw_dir"     : "/hercules/results/rwharton/mmgps_gc/raw",
            "results_dir" : "/hercules/results/rwharton/mmgps_gc/search",
            "src_dir"     : "/u/rwharton/src/searching/peasoup/v2"
        },
```

## Software
The pipeline requires [peasoup](https://github.com/ewanbarr/peasoup), 
[PulsarX](https://github.com/ypmen/PulsarX), and 
[TransientX](https://github.com/ypmen/TransientX). Instead of 
installing them proper, we opt instead to utilize them through 
singularity containers.  The location of the relevant singularity 
files is specified under the relevant task in the parameter file.
For example, under the filtool step:

```
"filtool" :
        {
            "sif" :
                {
                    "dir"  : "/hercules/results/rwharton/singularity_images",
                    "file" : "pulsarx_latest.sif"
                },
```

while this is done entirely out of laziness, it has the side 
benefit of ensuring repeatability (so long as you use the same 
singularity files).

## Processing Steps
The processing steps are at the top of the JSON file:

```
 "proc_steps" :
        {
            "filtool"       : true,
            "peasoup"       : true,
            "fold"          : true,
            "tx_sp_search"  : true,
            "tx_sp_filter"  : true
        },
```
The names of the steps denote a processing task that 
is to be done.  Simply put `true` if you want to run 
that step and `false` if you do not.  Each step has 
certain requirements that will be checked when it is 
run. The name of each step denotes a keyword later in 
the JSON file which contains the sif file path and 
processing arguments.


## Setting Options for each Task
The arguments to be run by each task are given 
under `opts` in the task dictionary.  So, for 
`peasoup` we have:

```
 "peasoup" :
        {
            "sif" :
                {
                    "dir"  : "/hercules/results/rwharton/singularity_images",
                    "file" : "peasoup_keplerian.sif"
                },

            "opts" :
                {
                    "num_threads" : 1,
                    "min_snr" : 7,
                    "acc_start" : -100,
                    "acc_end" : 100,
                    "ram_limit_gb" : 100.0,
                    "dm_start" : 500,
                    "dm_end" : 3000,
                    "nharmonics": 4,
                    "limit" : 1000,
                    "verbose": false
                }
        },
```

The first part points to the `sif` file, and the second 
part gives the keyword arguments that are passed to the 
`peasoup` task.  For simplicity (to me!), we are using the 
exact names to the double dashed keyword arguments.  So

```
"acc_end" : 100
```

corresponds to 

```
peasoup --acc_end 100
```

If you want to include a tag that does not accept an argument 
(e.g., the verbose tag), just include the keyword and add true, so

```
"verbose" : true
```

would give

```
peasoup --verbose
```

and `false` would just not include that tag.

By keeping this consistent usage, you can add any additional 
argument to this list so long as you use the `--` name.


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

## Running on a Cluster
The pipeline was written to be run on a node of a cluster. Because 
of this, we try to be careful about removing files on the node when
we are done.  So the general outline of the script is:

```
try:
    Copy over files to local area

    Do various processing steps 

    Copy the relevant files back to results directory 

except: 
    Catch exception if something fails

finally:
    Regardless of whether things worked or not, 
    delete everything from the working directory 
    on the remote node.
```

This makes sure we don't leave anything on the node, but can sometimes 
be a little annoying because intermediate products are lost if the 
pipeline fails at a later step.
