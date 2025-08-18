import os
import sys
import time
import json
import subprocess as sp
from glob import glob
import shutil
from datetime import datetime
from argparse import ArgumentParser


class Timer:
    def __init__(self):
        self.filtool = 0.0
        self.peasoup = 0.0
        self.fold    = 0.0
        self.sp      = 0.0
        self.total   = 0.0
        self.dstart  = ""
        self.dstop   = ""

    def print_summary(self):
        print("\n\n")
        print("****************************************************")
        print("                  TIME SUMMARY                      ")
        print("****************************************************")
        print("\n")
        print("Start Time: %s" %self.dstart)
        print("Stop Time:  %s" %self.dstop)
        print("\n")
        print("Program:                         Running Time (min): ")
        print("--------                         -----------------  ")
        print("filtool                          %.2f" %(self.filtool/60.))
        print("peasoup                          %.2f" %(self.peasoup/60.))
        print("fold                             %.2f" %(self.fold/60.))
        print("single pulse                     %.2f" %(self.sp/60.))
        print("\n")
        print("Total Runtime = %.2f min" %(self.total/60.))

    def write_summary(self, outfile):
        fout = open(outfile, 'w')
        fout.write( "****************************************************\n")
        fout.write( "                  TIME SUMMARY                      \n")
        fout.write( "****************************************************\n")
        fout.write( "\n"                                                    )
        fout.write( "Start Time: %s\n" %self.dstart)
        fout.write( "Stop Time:  %s\n" %self.dstop)
        fout.write( "\n"                                                     )
        fout.write( "Program:                         Running Time (min): \n")
        fout.write( "--------                         -----------------  \n")
        fout.write( "filtool                          %.2f\n" %(self.filtool/60.))
        fout.write( "peasoup                          %.2f\n" %(self.peasoup/60.))
        fout.write( "fold                             %.2f\n" %(self.fold/60.))
        fout.write( "single pulse                     %.2f\n" %(self.sp/60.))
        fout.write( "\n"                                                   )
        fout.write( "Total Runtime = %.2f min\n" %(self.total/60.))
        fout.close()


def check_file_exists(fpath):
    """
    Check if file exists, if not let us know, 
    and return a 0

    Otherwise, return 1
    """
    if not os.path.exists(fpath):
        print("File not found!")
        print(f"  {fpath}")
        print("Cannot proceed... exiting")
        retval = 0
    else: 
        print(f"Found file: {fpath}")
        retval = 1

    return retval


def read_and_check_json(jsonfile):
    """
    Read in JSON file, make sure that we have 
    options for each proc step and return 
    dictionary
    """
    print("==============================")
    print("  Checking Pipeline Options   ")
    print("==============================\n")

    # make sure it exists
    if not check_file_exists(jsonfile):
        return None

    # read file
    with open(jsonfile, 'r') as fin:
        jtxt = fin.read()
        
    # Convert from string to json dict
    d = json.loads(jtxt)

    # Make sure "proc_steps" exists
    if d.get('proc_steps') is None:
        print("No processing steps found!")
        return None

    # Make sure each True proc_step has 
    # an args dict
    pfails = 0
    for pkey, pval in d['proc_steps'].items():
        if pval is True:
            print(f"Requested step \'{pkey}\'")
            if d.get(pkey) is not None:
                print("  ...options found")
            else:
                print("   ...NO OPTIONS FOUND!")
                pfails += 1
        print('\n')

    if pfails > 0:
        return None

    return d 


def check_proc(jdict, proc_name):
    """ 
    Check to see if we are running "proc_name"
    """
    return jdict["proc_steps"].get(proc_name, False)
    
        
def dict_to_opts(opt_dict):
    """
    Convert dictionary of options to string
    """
    out_str = ""
    for key, val in opt_dict.items():
        if type(val) == bool:
            # If True, just retain as a flag
            # (ie, --key ) with no arg
            # If False, do not include opt
            if val == True:
                val = ""
            else:
                continue

        # add key + val to string
        out_str += f"--{key} {val} "

    return out_str


def get_and_check_sif(sif_dict):
    """
    Takes a dictionary that has keys 
    "dir" and "file".  Combines them 
    to a path, make sure it exists 
    and return it
    """
    sif_dir  = sif_dict.get('dir')
    sif_name = sif_dict.get('file')

    sif_file = ""
    retval = 1
    
    if sif_dir is None:
        print(f"sif[dir] not given!")
        retval = 0

    if sif_name is None:
        print(f"sif[file] given!")
        retval = 0

    if retval == 1:
        sif_file = f"{sif_dir}/{sif_name}" 
        retval = check_file_exists(sif_file)

    if retval == 0:
        sys.exit(0)

    return sif_file 


def format_name(name_dir):
    """
    Remove trailing '/' on path names (for consistency)
    """
    if(name_dir.endswith('/')):
        name_dir = name_dir.rstrip('/')
    return(name_dir)


def try_cmd(cmd, stdout=None, stderr=None):
    """
    Run the command in the string cmd using sp.run().  If there
    is a problem running, a CalledProcessError will occur and the
    program will quit.
    """
    print("\n\n %s \n\n" %cmd)
    try:
        retval = sp.run(cmd, shell=True, stdout=stdout, stderr=stderr)
    except sp.CalledProcessError:
        print("The command:\n %s \ndid not work, quitting..." %cmd)
        sys.exit(0)
    return 


def run_filtool(beamname, fil_dir, results_dir, jdict):
    """
    Run filtool on the input filterbank files, 
    producing one combined and rfi filtered file
    """
    t_start = time.time()

    # Get relevant process dict
    pd = jdict["filtool"]

    # Get sif file from arg dict
    ft_sif = get_and_check_sif(pd["sif"])

    # Get options from arg dict
    par_str = dict_to_opts(pd["opts"])

    # Set binds
    bstr = f"{fil_dir},{results_dir}"
    print(f"{bstr=}")

    # Get input fil files 
    glob_str = f"{fil_dir}/*_{beamname}_*fil"
    fil_files = glob(glob_str)
    fil_files.sort()
    if len(fil_files) == 0:
        print("No fil files found in:")
        print(f"    {fil_dir}")
        sys.exit(0)

    # Make fil file string
    fil_list_str = ' '.join(fil_files) 

    # Make output base name 
    outbase = f"{results_dir}/{beamname}"
    
    ft_cmd = f"filtool {par_str} -o {outbase} -s {beamname} " +\
             f"-f {fil_list_str}"
    print(f"\n{ft_cmd=}\n")
    sing_cmd = f"singularity exec --nv -B {bstr} {ft_sif} {ft_cmd}"
    #stderr = open('err.txt', 'a+')
    #stdout = open('out.txt', 'a+')

    #try_cmd(sing_cmd, stderr=stderr, stdout=stdout)
    try_cmd(sing_cmd)

    # will not fail properly because the thing INSIDE
    # singularity failed, not the singularity command
    # need to check output

    t_end = time.time()
    dt = t_end - t_start

    return dt


def run_peasoup(beamname, fil_dir, results_dir, jdict):
    """
    Run peasoup on the fil file
    """
    t_start = time.time()

    #Get relevant process dict
    pd = jdict["peasoup"]

    # Get sif file from arg dict
    ps_sif = get_and_check_sif(pd["sif"])

    # Get options from arg dict
    par_str = dict_to_opts(pd["opts"])

    # Set filterbank file name... filtools appends a _01 
    # this is ugly and hard coded
    filfile = f"{fil_dir}/{beamname}_01.fil" 
    if not check_file_exists(filfile):
        sys.exit(0)
    
    # Set binds
    if fil_dir == results_dir:
        bstr = f"{results_dir}"
    else:
        bstr = f"{fil_dir},{results_dir}"
    print(f"{bstr=}")
    
    ps_cmd = f"peasoup {par_str} -o {results_dir} " +\
             f"-i {filfile}"
    print(f"\n{ps_cmd=}\n")
    sing_cmd = f"singularity exec --nv -B {bstr} {ps_sif} {ps_cmd}"
    #stderr = open('err.txt', 'a+')
    #stdout = open('out.txt', 'a+')

    try_cmd(sing_cmd)

    # will not fail properly because the thing INSIDE
    # singularity failed, not the singularity command
    # need to check output

    t_end = time.time()
    dt = t_end - t_start

    return dt


def organize_fold_results(results_dir):
    """
    organize the output from peasoup folding
    
    pulsarx will produce a bunch of *png files, 
    corresponding *ar files, a filtered*csv file 
    and a pulsarx.candfile

    we'll make a directory called cand_plots 
    and put things there
    """
    out_dir = f"{results_dir}/cand_plots"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # move pngs
    png_files = glob(f"{results_dir}/*.png")
    for pp in png_files:
        shutil.move(pp, out_dir)

    # move archives
    ar_files = glob(f"{results_dir}/*.ar")
    for aa in ar_files:
        shutil.move(aa, out_dir)

    # move cand file
    cc_files =  glob(f"{results_dir}/*.cands") 
    cc_files.append(f"{results_dir}/pulsarx.candfile")
    cc_files.append(f"{results_dir}/filtered_df_for_folding.csv")

    for cc in cc_files:
        if os.path.exists(cc):
            shutil.move(cc, out_dir)    
        else:
            print("No such file:")
            print(f"  {cc}")

    return
        
     
def run_psrX_fold(beamname, fil_dir, results_dir, jdict):
    """
    Run peasoup on the fil file
    """
    t_start = time.time()

    # Get relevant process dict
    pd = jdict["fold"]

    # Get sif file from arg dict
    fold_sif = get_and_check_sif(pd["sif"])

    # Get options from arg dict
    par_str = dict_to_opts(pd["opts"])

    # Get the src dir
    src_dir = jdict["dirs"]["src_dir"]

    # Set filterbank file name... filtools appends a _01 
    # this is ugly and hard coded
    filfile = f"{fil_dir}/{beamname}_01.fil" 
    print(f"{filfile}")
    
    if not check_file_exists(filfile):
        sys.exit(0)

    # set path to template file
    temp_name = pd["template"]
    temp_file = f"{src_dir}/templates/{temp_name}"
    if not check_file_exists(temp_file):
        sys.exit(0)

    # Set binds
    if fil_dir == results_dir:
        bstr = f"{results_dir}"
    else:
        bstr = f"{fil_dir},{results_dir}"
    print(f"{bstr=}")
    
    fold_cmd = f"python {src_dir}/fold_cands.py " +\
               f"-i {results_dir}/overview.xml " +\
               f"{par_str} " +\
               f"-p {temp_file}"  
    print(f"\n{fold_cmd=}\n")
    sing_cmd = f"singularity exec -B {bstr} {fold_sif} {fold_cmd}"
    #stderr = open('err.txt', 'a+')
    #stdout = open('out.txt', 'a+')

    # will not fail properly because the thing INSIDE
    # singularity failed, not the singularity command
    # need to check output
    try_cmd(sing_cmd)

    # Make cands directory and move results there
    organize_fold_results(results_dir)
    

    t_end = time.time()
    dt = t_end - t_start

    return dt


def organize_sp_results(results_dir):
    """
    organize the output from TransientX SP search
    
    pulsarx will produce a bunch of *png files and 
    a cands file

    we'll make a directory called sp_plots 
    and put things there
    """
    out_dir = f"{results_dir}/sp_plots"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # make a directory for non sifted
    all_dir = f"{out_dir}/all"
    if not os.path.exists(all_dir):
        os.mkdir(all_dir)
    
    # make a directory for replot sifted
    sift_dir = f"{out_dir}/sifted"
    if not os.path.exists(sift_dir):
        os.mkdir(sift_dir)

    # Move over replot files first since they 
    # will all have "replot" in the name
    replot_files = glob(f"{results_dir}/*replot*")
    for rr in replot_files:
        shutil.move(rr, sift_dir)

    # everything else will be from before sifting
    # move pngs
    png_files = glob(f"{results_dir}/*.png")
    for pp in png_files:
        shutil.move(pp, all_dir)

    # move cand files
    cc_files =  glob(f"{results_dir}/*.cands") 

    for cc in cc_files:
        if os.path.exists(cc):
            shutil.move(cc, all_dir)    
        else:
            print("No such file:")
            print(f"  {cc}")

    return
        

def run_transientX(beamname, fil_dir, results_dir, jdict):
    """
    Run transientX single pulse search on fil file 
    and then run replot_fil to filter out duplicates
    """
    t_start = time.time()

    # Set filterbank file name... filtools appends a _01 
    # this is ugly and hard coded
    filfile = f"{fil_dir}/{beamname}_01.fil" 
    outbase = f"{beamname}"
    
    if not check_file_exists(filfile):
        sys.exit(0)
    
    # Set binds
    if fil_dir == results_dir:
        bstr = f"{results_dir}"
    else:
        bstr = f"{fil_dir},{results_dir}"
    print(f"{bstr=}")

    ############################
    ###  run transientx_fil  ###
    ############################
    if check_proc(jdict, "tx_sp_search"):
        # Get relevant process dict
        s_pd = jdict["tx_sp_search"]

        # Get sif file from arg dict
        s_sif = get_and_check_sif(s_pd["sif"])

        # Get options from arg dict
        s_par_str = dict_to_opts(s_pd["opts"])

        s_cmd = f"transientx_fil {s_par_str} -o {outbase} " +\
                f"-f {filfile}"
    
        print(f"\n{s_cmd=}\n")
        s_sing_cmd = f"singularity exec -B {bstr} {s_sif} {s_cmd}"

        try_cmd(s_sing_cmd)


    ########################
    ###  run replot_fil  ###
    ########################
    if check_proc(jdict, "tx_sp_filter"):
        # Get relevant process dict
        f_pd = jdict["tx_sp_filter"]

        # Get sif file from arg dict
        f_sif = get_and_check_sif(f_pd["sif"])

        # Get options from arg dict
        f_par_str = dict_to_opts(f_pd["opts"])
    
        # Get cands file
        cfiles = glob(f"{results_dir}/{outbase}*cands")

        if len(cfiles) == 1:
            cand_file = cfiles[0]
            f_cmd = f"replot_fil {f_par_str} " +\
                    f"--candfile {cand_file} -f {filfile}"
            print(f"\n{f_cmd=}\n")
            f_sing_cmd = f"singularity exec -B {bstr} {f_sif} {f_cmd}"
            try_cmd(f_sing_cmd)
    
        elif len(cfiles) == 0:
            print("single pulse candfile not found!")
            print("...skipping replot")
       
        else:
            print("too many candfiles found!")
            print(cfiles)
            print("...skipping replot")
    
    # Make cands directory and move results there
    organize_sp_results(results_dir)

    t_end = time.time()
    dt = t_end - t_start

    return dt
 

def setup(beamname, local_fil, local_results, 
          host_fil, host_results, jdict):
    """
    Setup HOST directories and copy over necessary files

    If we need to run filtool, then we will copy over 
    all the files in local_fil.

    If not, then a combined file should already 
    exist in local_results

    In this setup function, we will decide which files 
    are needed and move them over to the HOST accordingly
    """
    # Make HOST fil dir
    if not os.path.exists(host_fil):
        os.makedirs(host_fil)

    # Make HOST results dir 
    if not os.path.exists(host_results):
        os.makedirs(host_results)

    # If we are running filtool, then copy over 
    # all the fil files of the form:
    #  *_{beamname}_*.fil
    if check_proc(jdict, "filtool"):
        glob_str = f"{local_fil}/*_{beamname}_*fil"
        fil_list = glob(glob_str)
        fil_list.sort()
        
        print("\n\nLooking for fil files in:")
        print(f"   {local_fil}")
        print(f"   Matching on {glob_str}")
        print(f"Found {len(fil_list)} fil files:")
        for ffn in fil_list:
            print(ffn)

        if len(fil_list) == 0:
            sys.exit(0)

        # Copy over fil files to HOST_FIL
        print("\nCOPYING OVER FIL FILES")
        for ffn in fil_list:
            shutil.copy(ffn, host_fil)
        
    # If we are NOT running filtool then the combined 
    # data file should already exist in LOCAL_RESULTS,
    # so we can just copy it over
    elif (check_proc(jdict, "peasoup") or check_proc(jdict, "fold")):
        glob_str = f"{local_results}/{beamname}*.fil"
        fil_list = glob(glob_str)
        fil_list.sort()
        
        print("\n\nLooking for fil files in:")
        print(f"   {local_fil}")
        print(f"   Matching on {glob_str}")
        print(f"Found {len(fil_list)} fil files:")
        for ffn in fil_list:
            print(ffn)

        if len(fil_list) == 0:
            sys.exit(0)

        if len(fil_list) > 1:
            print(f"Only expected one file, found {len(fil_list)}")
            sys.exit(0) 

        # Copy over fil files to HOST_FIL
        print("COPYING OVER FIL FILE")
        shutil.copy(fil_list[0], host_results)

    else: pass
    
    return


def get_results(local_results, host_results):
    """
    Copy over files from HOST to LOCAL
    """
    # Check for and copy directories
    sub_dirs = ["cand_plots", "sp_plots"]
    for sub_dir in sub_dirs:
        local_path = "%s/%s" %(local_results, sub_dir)
        host_path  = "%s/%s" %(host_results, sub_dir)
        if not os.path.exists(local_path):
            if os.path.exists(host_path):
                shutil.copytree(host_path, local_path)
            else: pass
        else: pass

    # Check for log files
    log_files = glob("%s/*log" %(host_results))
    # Check for xml files 
    xml_files = glob("%s/*xml" %(host_results))
    
    misc_files = log_files + xml_files

    # Copy them over
    if len(misc_files):
        for mm_file in misc_files:
            print(mm_file)
            fname = mm_file.split('/')[-1]
            shutil.copyfile(mm_file, "%s/%s" %(local_results, fname))
    else: pass

    return


def cleanup(host_fil, host_results):
    """
    Remove remaining files from HOST
    """
    if os.path.exists(host_fil):
        print("REMOVING HOST FIL FILES in %s\n" %host_fil)
        shutil.rmtree(host_fil)
    else: pass
    
    if os.path.exists(host_results):
        print("REMOVING HOST RESULTS in %s\n" %host_results)
        shutil.rmtree(host_results)
    else: pass

    return 


def cleanup_beam(beam_host):
    """
    Remove remaining files from HOST
    """
    if os.path.exists(beam_host):
        print("REMOVING DIRECTORY %s" %beam_host)
        shutil.rmtree(beam_host)
    else: pass
    
    return 

def copy_and_tag_json(jsonfile, local_results):
    """
    Copy json file to results directory and append 
    a date time tag 
    """
    dnow = datetime.now() 
    dstr = dnow.strftime('%Y%m%dT%H%M%S')
   
    if os.path.exists(jsonfile): 
        fname = jsonfile.split('/')[-1]
        fbase = fname.rsplit('.json')[0]

        outfile = f"{local_results}/{fbase}_{dstr}.json"
            
        shutil.copyfile(jsonfile, outfile)

    return 
    
    
def print_dirs(h_top, h_fil, h_results, l_fil, l_results):
    print("\n\n")
    print("========== HOST ===========")
    print(" TOP     = %s" %h_top)
    print(" FIL     = %s" %h_fil)
    print(" RESULTS = %s" %h_results)
    print("===========================")
    print("\n\n")
    print("========== LOCAL ===========")
    print(" FIL     = %s" %l_fil)
    print(" RESULTS = %s" %l_results)
    print("===========================")
    print("\n\n")
    return 


def parse_input():
    """
    Parse argumnents to GC Search Pipeline
    """
    prog_desc = "GC Search Pipeline using Peasoup and TransientX"
    parser = ArgumentParser(description=prog_desc)

    parser.add_argument('--work_dir', 
                        help='Path to work directory',
                        required=True)
    parser.add_argument('--args_json', 
                        help='JSON file containing pipeline args',
                        required=True)
    parser.add_argument('--beam',
                        help='Beam number',
                        required=True, type=int, default=0)
    args = parser.parse_args()

    return args


####################
##     MAIN       ##
####################

if __name__ == "__main__":
    # Start Timer
    tt = Timer()
    t_start = time.time()

    # Get date time start 
    dstart = datetime.now() 
    tt.dstart = dstart.strftime('%Y-%m-%dT%H:%M:%S')

    # Parse input
    args = parse_input()
    
    # beam name
    beam_num = args.beam
    beamname = f"cfbf{beam_num:05d}"

    # Read in the json args file and make sure its ok
    # It will return None if something went wrong
    jsonfile = args.args_json
    jd = read_and_check_json(jsonfile)
    if jd is None:
        sys.exit(0)

    # Relevant directories on compute node
    top_HOST     = format_name( args.work_dir )
    beam_HOST    = f"{top_HOST}/{beamname}"
    fil_HOST     = f"{beam_HOST}/fil"
    results_HOST = f"{beam_HOST}/search"

    # Relevant directories on local space
    raw_dir       = format_name( jd["dirs"]["raw_dir"] )
    fil_LOCAL     = f"{raw_dir}/{beamname}"
    
    results_dir   = format_name( jd["dirs"]["results_dir"] )
    results_LOCAL = f"{results_dir}/{beamname}"
   
    # print path info
    print_dirs(top_HOST, fil_HOST, results_HOST, 
               fil_LOCAL, results_LOCAL)

    # TRY SETTING UP AND SEARCHING
    try:
        # SET-UP on HOST 
        setup(beamname, fil_LOCAL, results_LOCAL, 
              fil_HOST, results_HOST, jd)

        print(f"Files in {fil_HOST}:", glob("%s/*" %fil_HOST), "\n")
        print(f"Files in {results_HOST}:", glob("%s/*" %results_HOST), "\n")

        # Go to results directory
        os.chdir(results_HOST)
        # print current working directory
        print("Currently in: ", os.getcwd(), "\n")

        # run filtool to combine + clean files
        # prelim fil files will be in fil_HOST, 
        # the result will be placed in results_HOST
        if check_proc(jd, "filtool"):
            dt_ft = run_filtool(beamname, fil_HOST, results_HOST, jd)
            tt.filtool = dt_ft
   
        # run psoup fourier domain periodicity search     
        if check_proc(jd, "peasoup"):
            dt_ps = run_peasoup(beamname, results_HOST, results_HOST, jd)
            tt.peasoup = dt_ps
   
        # run pulsarX candidate folding 
        if check_proc(jd, "fold"):
            dt_fold = run_psrX_fold(beamname, results_HOST, results_HOST, jd)
            tt.fold = dt_fold

        # run TransientX single pulse search
        if check_proc(jd, "tx_sp_search") or  check_proc(jd, "tx_sp_filter"):
            dt_sp = run_transientX(beamname, results_HOST, results_HOST, jd)
            tt.sp = dt_sp

        # Copy back results
        get_results(results_LOCAL, results_HOST)

    except:
        print("Something failed!!!!")

    finally:
        # Delete everything from compute node
        cleanup_beam(beam_HOST)

        # Finish up time profiling and print summary to screen
        t_finish = time.time()
        tt.total = t_finish - t_start
    
        # Get date time end
        dstop = datetime.now() 
        tt.dstop = dstop.strftime('%Y-%m-%dT%H:%M:%S')
        
        tt.print_summary()
        dstr = dstop.strftime('%Y%m%dT%H%M%S')
        logname = f"{beamname}_{dstr}.log"
        tt.write_summary(f"{results_LOCAL}/{logname}")

        # Copy JSON file to results
        copy_and_tag_json(jsonfile, results_LOCAL)

        print("done")
