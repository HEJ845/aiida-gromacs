#!/usr/bin/env python
"""CLI utility to run gmx mdrun with AiiDA.

Usage: gmx_mdrun --help
"""

import os

import click

from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers


def launch(params):
    """Run mdrun.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # If code is not initialised, then setup.
    gromacs_code = params.pop("code")
    if not gromacs_code:
        computer = helpers.get_computer()
        gromacs_code = helpers.get_code(entry_point="gromacs", computer=computer)

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    tprfile = SinglefileData(file=os.path.join(os.getcwd(), params.pop("s")))

    MdrunParameters = DataFactory("gromacs.mdrun")
    parameters = MdrunParameters(params)

    # set up calculation.
    inputs = {
        "code": gromacs_code,
        "parameters": parameters,
        "tprfile": tprfile,
        "metadata": {
            "description": "mdrun minimisation job submission with the aiida_gromacs plugin",
        },
    }

    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    future = engine.submit(CalculationFactory("gromacs.mdrun"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Input file options
@click.option("-s", default="topol.tpr", type=str, help="Portable xdr run input file")
@click.option("-cpi", type=str, help="Checkpoint file")
@click.option("-table", type=str, help="xvgr/xmgr file")
@click.option("-tablep", type=str, help="xvgr/xmgr file")
@click.option("-tableb", type=str, help="xvgr/xmgr file")
@click.option("-rerun", type=str, help="Trajectory: xtc trr cpt gro g96 pdb tng")
@click.option("-ei", type=str, help="ED sampling input")
@click.option("-multidir", type=str, help="Run directory")
@click.option("-awh", type=str, help="xvgr/xmgr file")
@click.option("-membed", type=str, help="Generic data file")
@click.option("-mp", type=str, help="Topology file")
@click.option("-mn", type=str, help="Index file")
# Output file options
@click.option("-o", default="topol.gro", type=str, help="Trajectory output file")
@click.option("-x", type=str, help="Compressed trajectory (tng format or portable xdr format)")
@click.option("-cpo", type=str, help="Checkpoint file")
@click.option("-c", default="confout.gro", type=str, help="Structure file")
@click.option("-e", default="ener.edr", type=str, help="Energy file")
@click.option("-g", default="md.log", type=str, help="MD log file")
@click.option("-dhdl", type=str, help="xvgr/xmgr file")
@click.option("-field", type=str, help="xvgr/xmgr file")
@click.option("-tpi", type=str, help="xvgr/xmgr file")
@click.option("-tpid", type=str, help="xvgr/xmgr file")
@click.option("-eo", type=str, help="xvgr/xmgr file")
@click.option("-px", type=str, help="xvgr/xmgr file")
@click.option("-pf", type=str, help="xvgr/xmgr file")
@click.option("-ro", type=str, help="xvgr/xmgr file")
@click.option("-ra", type=str, help="Log file")
@click.option("-rs", type=str, help="Log file")
@click.option("-rt", type=str, help="Log file")
@click.option("-mtx", type=str, help="Hessian matrix")
@click.option("-if", type=str, help="xvgr/xmgr file")
@click.option("-swap", type=str, help="xvgr/xmgr file")
# Other parameters
@click.option("-xvg", default="false", type=str, help="xvg plot formatting: xmgrace, xmgr, none")
@click.option("-dd", type=str, help="Domain decomposition grid, 0 is optimize")
@click.option("-ddorder", type=str, help="DD rank order: interleave, pp_pme, cartesian")
@click.option("-npme", type=str, help="Number of separate ranks to be used for PME, -1 is guess")
@click.option("-nt", type=str, help="Total number of threads to start (0 is guess)")
@click.option("-ntmpi", type=str, help="Number of thread-MPI ranks to start (0 is guess)")
@click.option("-ntomp", type=str, help="Number of OpenMP threads per MPI rank to start (0 is guess)")
@click.option("-ntomp_pme", type=str, help="Number of OpenMP threads per MPI rank to start (0 is -ntomp)")
@click.option("-pin", type=str, help="Whether mdrun should try to set thread affinities: auto, on, off")
@click.option("-pinoffset", type=str, help="The lowest logical core number to which mdrun should pin the first thread")
@click.option("-pinstride", type=str, help="Pinning distance in logical cores for threads, use 0 to minimize the number of threads per physical core")
@click.option("-gpu_id", type=str, help="List of unique GPU device IDs available to use")
@click.option("-gputasks", type=str, help="List of GPU device IDs, mapping each PP task on each node to a device")
@click.option("-ddcheck", type=str, help="Check for all bonded interactions with DD")
@click.option("-rdd", type=str, help="The maximum distance for bonded interactions with DD (nm), 0 is determine from initial coordinates")
@click.option("-rcon", type=str, help="Maximum distance for P-LINCS (nm), 0 is estimate")
@click.option("-dlb", type=str, help="Dynamic load balancing (with DD): auto, no, yes")
@click.option("-dds", type=str, help="Fraction in (0,1) by whose reciprocal the initial DD cell size will be increased in order to provide a margin in which dynamic load balancing can act while preserving the minimum cell size.")
@click.option("-nb", type=str, help="Calculate non-bonded interactions on: auto, cpu, gpu")
@click.option("-nstlist", type=str, help="Set nstlist when using a Verlet buffer tolerance (0 is guess)")
@click.option("-tunepme", type=str, help="Optimize PME load between PP/PME ranks or GPU/CPU")
@click.option("-pme", type=str, help="Perform PME calculations on: auto, cpu, gpu")
@click.option("-pmefft", type=str, help="Perform PME FFT calculations on: auto, cpu, gpu")
@click.option("-bonded", type=str, help="Perform bonded calculations on: auto, cpu, gpu")
@click.option("-update", type=str, help="Perform update and constraints on: auto, cpu, gpu")
@click.option("-v", type=str, help="Be loud and noisy")
@click.option("-pforce", type=str, help="Print all forces larger than this (kJ/mol nm)")
@click.option("-reprod", type=str, help="Try to avoid optimizations that affect binary reproducibility")
@click.option("-cpt", type=str, help="Checkpoint interval (minutes)")
@click.option("-cpnum", type=str, help="Keep and number checkpoint files")
@click.option("-append", type=str, help="Append to previous output files when continuing from checkpoint instead of adding the simulation part number to all file names")
@click.option("-nsteps", type=str, help="Run this number of steps (-1 means infinite, -2 means use mdp option, smaller is invalid)")
@click.option("-maxh", type=str, help="Terminate after 0.99 times this time (hours)")
@click.option("-replex", type=str, help="Attempt replica exchange periodically with this period (steps)")
@click.option("-nex", type=str, help="Number of random exchanges to carry out each exchange interval (N^3 is one suggestion). -nex zero or not specified gives neighbor replica exchange.")
@click.option("-reseed", type=str, help="Seed for replica exchange, -1 is generate a seed")
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    # pylint: disable=line-too-long
    """Run example.

    Example usage:

    $ gmx_mdrun --code gmx@localhost -s 1AKI_em.tpr -c 1AKI_minimised.gro -e 1AKI_minimised.edr -g 1AKI_minimised.log -o 1AKI_minimised.trr

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_mdrun -s 1AKI_em.tpr -c 1AKI_minimised.gro -e 1AKI_minimised.edr -g 1AKI_minimised.log -o 1AKI_minimised.trr

    Help: $ gmx_mdrun --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
