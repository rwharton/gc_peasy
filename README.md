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


