# Important paths
# Let's use a directory structure that is like this:
#
# 4x5 min non-filtool-ed fil files for all obs are in
#
#         raw_dir/cfbfXXXXX/
#
# Combined and filtool cleaned 20min fil file will be in:
#
#         results_dir/cfbfXXXXX/
# 
# and will be called cfbfXXXXX.fil
#
# The peasoup search results will be an xml file that is 
# also in the results directory
#
# When we fold we will put the results in:
#
#         results_dir/cfbfXXXXX/cands
#
# So this means that the `raw_dir` and `results_dir` 
# given below are the TOP directories, the beam directories
# will be created as necessary

raw_dir     = "/hercules/results/rwharton/mmgps_gc/raw"
results_dir = "/hercules/results/rwharton/mmgps_gc/search"
beamname = "cfbf00088"

# Singularity files
sing_dir    = "/hercules/results/rwharton/singularity_images"
peasoup_sif = "%s/peasoup_keplerian.sif" %sing_dir
psrx_sif    = "%s/pulsarx_latest.sif" %sing_dir

# Resume previous processing?
resume    = 0
copy_fil  = 0


# Processing steps to do
do_filtool    = 0      # Run filtool 
do_peasoup    = 1      # Run PEASOUP search
do_fold       = 0      # Fold data

# Filtool
ftool_opts = ''

# Peasoup options 
#peasoup -i data.fil \
#        --fft_size 67108864 \
#        --limit 100000 \
#        -m 7.0 \
#        -o output_dir \
#        -t 1 \
#        --acc_start -50 \
#        --acc_end 50 \
#        --dm_file my_dm_trials.txt \
#        --ram_limit_gb 180.0 \
#        -n 4
psoup_opts = '-m 7.0 -t 1 --acc_start -100 --acc_end 100 --ram_limit_gb 20.0 --dm_start 500 --dm_end 3000 -n 8' 


