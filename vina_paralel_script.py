import argparse
import glob
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os.path import isdir, exists, join, splitext, basename
from pathlib import Path
from subprocess import run
from sys import platform

"""
This script assumes the folder containing ligands (variable :liglib:) is in the path (current working directory).
Same applies for the receptor (variable :receptor:) and for the Vina configuration file (variable :conf:).
Note: Argument --cpu should not be used in the configuration file as it is passed while calling vina.exe
:vina:      path to vina.exe executable
:outputdir: path to save docking outputs *.pdbqt and *.out files
:core_in:   number of core used for each ligand (equivalent to vina --cpu setting)
:par_run:   number of parallel runs to be used
"""


def validate_inputs(receptor, liglib, conf, vina):
    if not isdir(liglib):
        input("Directory with ligands ({}) not found. Exiting...".format(liglib))
        exit()
    if not exists(receptor):
        input("Receptor {} not found. Exiting...".format(receptor))
        exit()
    if not exists(conf):
        input("Configuration file {} not found. Exiting...".format(conf))
        exit()
    if not exists(vina):
        input("Vina executable {} not found in current folder. Exiting...".format(vina))
        exit()


def run_vina(lig):
    """
    Docking function, checking for previously succesfull docking runs.

    :lig:   ligand to dock
    """
    global vina, PIPE, core_in, conf, receptor, outputdir
    filename = splitext(basename(lig))[0]

    command = vina + ' --cpu "{0}" --config "{1}" --receptor "{2}" --ligand "{3}" --out "{4}_out.pdbqt" > "{4}.out"'.format(core_in, conf, receptor, lig, Path(outputdir, filename))

    if exists(Path(outputdir, filename + "_out.pdbqt")) and exists(Path(outputdir, filename + ".out")):
        with open(Path(outputdir, filename + ".out"), "r") as log:
            for line in log:
                if "***************************************************" in line.strip():
                    PIPE.write("Ligand already docked: {}.pdbqt\n".format(filename))

                    # print("Ligand already docked: {}.pdbqt".format(filename))
                    return

    PIPE.write("Docking: {}\n".format(filename))

    run(command, stdout=PIPE, stderr=PIPE, shell=True)


def parse_cmd():

    parser = argparse.ArgumentParser(description="Python parallel docking using AutoDock Vina")

    parser.add_argument('--receptor',
                        type=str, nargs=1,
                        default=None,
                        help='receptor to be used (default first *.pdbqt file in current directory)')
    parser.add_argument('--ligands',
                        type=str, nargs=1,
                        default=None,
                        help='folder containing ligands *.pdbqt files')
    parser.add_argument('--outputdir',
                        type=str, nargs=1,
                        default=None,
                        help='folder to save docking results')
    parser.add_argument('--conf',
                        type=str, nargs=1,
                        default=None,
                        help='Vina configuration file')

    return vars(parser.parse_args())


if __name__ == "__main__":
    # print("""Usage: vina_paralel_new2.py receptor [path_to_ligands/]""")
    print("Current working directory:", os.getcwd())

    args = parse_cmd()

    if platform == "linux" or platform == "linux2":
        vina = "./vina_1.2.3_linux_x86_64"
    elif platform == "darwin":
        pass
        # OS X
    elif platform == "win32":
        try:
            vina = glob.glob("vina*.exe")[0]
        except:
            pass
        # vina = "vina_1.2.3_windows_x86_64.exe"
        print(f"Vina binary to be used: {vina}")

    receptor, liglib, outputdir, conf = args["receptor"], args["ligands"], args["outputdir"], args["conf"]

    if receptor is None: receptor = glob.glob("*receptor*.pdbqt")[0]
    if liglib is None: liglib = "Ligands/"
    if outputdir is None: outputdir = liglib + "docked/"
    if conf is None: conf = glob.glob("*config*.*")[0]

    par_run = input("Set number of concurrent runs:(4) ")
    core_in = input("Set number of cores per run:  (1) ")
    if par_run == "":
        par_run = 4
    if core_in == "":
        core_in = 1

    validate_inputs(receptor, liglib, conf, vina)

    try:
        os.mkdir(outputdir)
        print("Created output folder {}".format(outputdir))
    except FileExistsError:
        pass
        # print(f"Outputs will be saved to {outputdir}...")
    print(f"Outputs will be saved to {outputdir}...")

    ligs = glob.glob(join(liglib, "*.pdbqt"))

    print(f"""\nPARAMETERS OF Vina RUN:
    Vina executable:    {vina}
    Cores per ligand:   {core_in} (done internally by Vina)
    Parallel runs:      {par_run}
    Receptor:           {receptor}
    Configuration file: {conf}
    Ligands folder:     {liglib} (found {len(ligs)} ligands)
    Outputs path:       {outputdir}""")

    #
    input("Press any key to start...")
    starttime = datetime.now()
    print("\nDocking started: {0}".format(starttime.time()))
    PIPE = open("vina_paralel_new.log", "w+")
    with ThreadPoolExecutor(max_workers=int(par_run)) as executor:
        executor.map(run_vina, ligs, timeout=10)
    endtime = datetime.now()
    difference = endtime - starttime
    PIPE.close()
    #

    print("\nDocking started: {0}".format(starttime.time()))
    print("Docking ended: {0}\nTotal time: {1}".format(endtime.time(), difference))
    print(f"Docked {len(ligs)} compounds.")
    input("Press any key to exit...")
