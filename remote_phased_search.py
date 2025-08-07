import os
import sys
import time
import remote_phased_params as params
import subprocess as sp
from glob import glob
import shutil

class Timer:
    def __init__(self):
        self.filtool = 0.0
        self.peasoup = 0.0
        self.fold    = 0.0
        self.total   = 0.0

    def print_summary(self):
        print("****************************************************")
        print("                  TIME SUMMARY                      ")
        print("****************************************************")
        print("\n")
        print("Program:                         Running Time (min): ")
        print("--------                         -----------------  ")
        print("filtool                          %.2f" %(self.filtool/60.))
        print("peasoup                          %.2f" %(self.peasoup/60.))
        print("\n")
        print("Total Runtime = %.2f min" %(self.total/60.))

    def write_summary(self, outfile):
        fout = open(outfile, 'w')
        fout.write( "****************************************************\n")
        fout.write( "                  TIME SUMMARY                      \n)")
        fout.write( "****************************************************\n)")
        fout.write( "\n"                                                     )
        fout.write( "Program:                         Running Time (min): \n")
        fout.write( "--------                         -----------------  \n")
        fout.write( "filtool                          %.2f\n" %(self.filtool/60.))
        fout.write( "peasoup                          %.2f\n" %(self.peasoup/60.))
        fout.write( "\n"                                                   )
        fout.write( "Total Runtime = %.2f min\n" %(self.total/60.))
        fout.close()


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


def run_filtool(beamname, fil_dir, results_dir):
    """
    Run filtool on the input filterbank files, 
    producing one combined and rfi filtered file
    """
    t_start = time.time()

    ft_sif = params.psrx_sif
    par_str = params.ftool_opts

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
    print(f"{ft_cmd=}")
    #ft_cmd = "ls /results /data"
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


def run_peasoup(beamname, fil_dir, results_dir):
    """
    Run peasoup on the fil file
    """
    t_start = time.time()

    ps_sif = params.peasoup_sif
    par_str = params.psoup_opts

    # Set filterbank file name... filtools appends a _01 
    # this is ugly and hard coded
    filfile = f"{fil_dir}/{beamname}_01.fil" 
    
    # Set binds
    if fil_dir == results_dir:
        bstr = f"{results_dir}"
    else:
        bstr = f"{fil_dir},{results_dir}"
    print(f"{bstr=}")
    
    ps_cmd = f"peasoup {par_str} -o {results_dir} " +\
             f"-i {filfile}"
    print(f"{ps_cmd=}")
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


#def organize_results(work_dir):
#    """
#    Put *out + *err files into a directory
#
#    Put *dat + *fft + *inf files into a directory
#    """
#    out_dir = "%s/output_files" %(work_dir)
#
#    # Collect all errs and outs
#    ostr_list = ["out", "err"]
#    for ostr in ostr_list:
#        ofiles = glob("%s/*%s" %(work_dir, ostr))
#        if len(ofiles):
#            # If files exist and out_dir doesnt, make it
#            if not os.path.exists(out_dir):
#                os.makedirs(out_dir)
#            for ofile in ofiles:
#                shutil.move(ofile, out_dir)
#        else: pass
#
#    # Collect all infs, dats, and ffts
#    dmstr_list = ["inf", "dat", "fft"]
#    for dmstr in dmstr_list:
#        dmfiles = glob("%s/*%s" %(work_dir, dmstr))
#        dm_dir = "%s/dm_%s" %(work_dir, dmstr)
#        if len(dmfiles):
#            # If files exist and dm_dir doesnt, make it
#            if not os.path.exists(dm_dir):
#                os.makedirs(dm_dir)
#            for dmfile in dmfiles:
#                shutil.move(dmfile, dm_dir)
#        else: pass
#
#    return
#    

def search_beam(filname, fil_dir, work_dir):
    tt = Timer()
    t_start = time.time()
    
    print("Results Directory: %s\n" %work_dir)
    print("fil Directory: %s\n" %fil_dir)
    print("File Name: %s\n" %filname)
    
    # Check to see if results directory exists. If not, create it.
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    
    # If we haven't done so already, go to results directory
    os.chdir(work_dir)

    if params.do_peasoup:
        dt_ps = run_peasoup(filname, fil_dir, work_dir)
    
    # Organize stray files into folders
    #organize_results(work_dir)

    # Finish up time profiling and print summary to screen
    t_finish = time.time()
    tt.total = t_finish - t_start
    tt.print_summary()
    tt.write_summary("%s.log" %filname)

    return


def setup(beamname, local_fil, local_results, host_fil, host_results):
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
    if params.do_filtool:
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
        print("COPYING OVER FIL FILES")
        for ffn in fil_list:
            shutil.copy(ffn, host_fil)
        
    # If we are NOT running filtool then the combined 
    # data file should already exist in LOCAL_RESULTS,
    # so we can just copy it over
    elif (params.do_peasoup or params.do_fold):
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
    sub_dirs = ["cands_presto", "dm_dat", "dm_inf", "dm_fft", 
                "output_files", "rfi_products", "single_pulse"]
    for sub_dir in sub_dirs:
        local_path = "%s/%s" %(local_results, sub_dir)
        host_path  = "%s/%s" %(host_results, sub_dir)
        if not os.path.exists(local_path):
            if os.path.exists(host_path):
                shutil.copytree(host_path, local_path)
            else: pass
        else: pass

    # Check for and copy log file
    log_files = glob("%s/*log" %(host_results))
    if len(log_files):
        for log_file in log_files:
            fname = log_file.split('/')[-1]
            shutil.copyfile(log_file, "%s/%s" %(local_results, fname))
    else: pass
    
    return


def cleanup(host_fil, host_results):
    """
    Remove remaining files from HOST
    """
    if os.path.exists(host_fil):
        print("REMOVING HOST FIL FILES in %s" %host_fil)
        shutil.rmtree(host_fil)
    else: pass
    
    if os.path.exists(host_results):
        print("REMOVING HOST RESULTS in %s" %host_results)
        shutil.rmtree(host_results)
    else: pass

    return 


def print_dirs(h_top, h_fil, h_results, l_fil, l_results):
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



####################
##     MAIN       ##
####################


if __name__ == "__main__":
    # Start Timer
    tt = Timer()
    t_start = time.time()
    
    # beam name
    beamname = params.beamname

    # Relevant directories on compute node
    top_HOST     = sys.argv[1]
    fil_HOST     = f"{top_HOST}/{beamname}/fil"
    results_HOST = f"{top_HOST}/{beamname}/search"

    # Relevant directories on local space
    fil_LOCAL     = f"{params.raw_dir}/{beamname}"
    results_LOCAL = f"{params.results_dir}/{beamname}"
   
    # print path info
    print_dirs(top_HOST, fil_HOST, results_HOST, 
               fil_LOCAL, results_LOCAL)

    # TRY SETTING UP AND SEARCHING
    try:
        # SET-UP on HOST 
        setup(beamname, fil_LOCAL, results_LOCAL, 
              fil_HOST, results_HOST)

        print(glob("%s/*" %fil_HOST))
        print(glob("%s/*" %results_HOST))

        # run filtool to combine + clean files
        # prelim fil files will be in fil_HOST, 
        # the result will be placed in results_HOST
        if params.do_filtool:
            dt_ft = run_filtool(beamname, fil_HOST, results_HOST)
            tt.filtool = dt_ft
        
        if params.do_peasoup:
            dt_ps = run_peasoup(beamname, results_HOST, results_HOST)
            tt.peasoup = dt_ps

        #print(glob("%s/*" %results_HOST))
    
        # Copy back results
        #get_results(results_LOCAL, results_HOST)

    except:
        print("Something failed!!!!")

    finally:
        # Delete everything from compute node
        print("done")
        #cleanup(fil_HOST, results_HOST)
        # Finish up time profiling and print summary to screen
        t_finish = time.time()
        tt.total = t_finish - t_start
        tt.print_summary()
        tt.write_summary("%s.log" %beamname)

