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

# Top of the source directory
src_dir = "/u/rwharton/src/searching/peasoup"

# Singularity files
sing_dir    = "/hercules/results/rwharton/singularity_images"
peasoup_sif = "%s/peasoup_keplerian.sif" %sing_dir
psrX_sif    = "%s/pulsarx_latest.sif" %sing_dir


# Processing steps to do
do_filtool    = 1      # Run filtool 
do_peasoup    = 1      # Run PEASOUP search
do_fold       = 1      # Fold data
do_sp         = 1      # Single Pulse Search with TransientX

# Filtool
ftool_opts = '-t 24 -z kadaneF 4 8 zdot'

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
psoup_opts = '-m 7.0 -t 2 --acc_start -100 --acc_end 100 --ram_limit_gb 20.0 --dm_start 500 --dm_end 3000 -n 4' 

# PulsarX folding
# Using COMPACT peasoup candidate folding script 
# Run as: 
# python /src/fold_cands.py -i $SEARCH/overview.xml 
#         -t pulsarx -p /src/templates/meerkat_fold_S4.template
#
# template should be in {src_dir}/templates/
fold_template = "meerkat_fold_S4.template"
psrX_opts = ""

# TransientX options
#transientx_fil -v -o [outbase] 
#               -t 12 --zapthre 3.0 --fd 1 --overlap 0.1 
#               --dms 1000 --ddm 10 --ndm 200 --thre 7 
#               --maxw 0.1 --snrloss 0.1 -l 2.0 --drop -z kadaneF 
#               8 4 zdot 
#               -f cfbf00088_01.fil

# all options besides outbase name and infile name
tX_opts = "-v -t 24 --zapthre 3.0 --fd 1 --overlap 0.1 --dms 500 --ddm 10 --ndm 300 --thre 7 --maxw 0.1 --snrloss 0.1 -l 2.0 --drop -z kadaneF 8 4 zdot" 
# replot
#replot_fil -v -t 4 --zapthre 3.0 --td 1 --fd 1 --dmcutoff 3 --widthcutoff 0.1 --snrcutoff 7 --snrloss 0.1 --zap --zdot --kadane 8 4 7 --candfile test.cands --clean -f *.fil
