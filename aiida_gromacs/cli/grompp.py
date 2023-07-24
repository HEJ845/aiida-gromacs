#!/usr/bin/env python
"""CLI utility to run gmx grompp with AiiDA.

Usage: gmx_grompp --help
"""

import os

import click

from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run grompp.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
        },
    }

    # If code is not initialised, then setup.
    inputs["code"] = params.pop("code")
    if not inputs["code"]:
        computer = helpers.get_computer()
        inputs["code"] = helpers.get_code(entry_point="gromacs", computer=computer)

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    inputs["mdpfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))
    inputs["grofile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("c")))
    inputs["topfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("p")))

    if "r" in params:
        inputs["r_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("r")))

    if "rb" in params:
        inputs["rb_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("rb")))

    if "n" in params:
        inputs["n_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("n")))
  
    if "t" in params:
        inputs["t_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("t")))

    if "e" in params:
        inputs["e_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("e")))

    if "qmi" in params:
        inputs["qmi_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("qmi")))

    if "ref" in params:
        inputs["ref_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("ref")))

    GromppParameters = DataFactory("gromacs.grompp")
    inputs["parameters"] = GromppParameters(params)


    # check if inputs are outputs from prev processes
    inputs = searchprevious.get_prev_inputs(inputs, ["grofile", "topfile", "mdpfile"])

    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    future = engine.submit(CalculationFactory("gromacs.grompp"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
@click.option("--description", default="record grompp data provenance via the aiida_gromacs plugin", type=str, help="Short metadata description")
# Input file options
@click.option("-f", default="grompp.mdp", type=str, help="Input parameter file")
@click.option("-c", required=True, type=str, help="Input structure file")
@click.option("-r", type=str, help="Structure file: gro g96 pdb brk ent esp tpr")
@click.option("-rb", type=str, help="Structure file: gro g96 pdb brk ent esp tpr")
@click.option("-n", type=str, help="Index file")
@click.option("-p", default="topol.top", type=str, help="Topology file")
@click.option("-t", type=str, help="Full precision trajectory: trr cpt tng")
@click.option("-e", type=str, help="Energy file")
@click.option("-qmi", type=str, help="Input file for QM program")
@click.option("-ref", type=str, help="Full precision trajectory: trr cpt tng")
# Output file options
@click.option("-o", default="conf.gro", type=str, help="Output structure file")
@click.option("-po", type=str, help="grompp input file with MD parameters")
@click.option("-pp", type=str, help="Topology file")
@click.option("-imd", type=str, help="Coordinate file in Gromos-87 format")
# Other parameter options
@click.option("-v", type=str, help="Be loud and noisy")
@click.option("-time", type=str, help="Take frame at or first after this time.")
@click.option("-rmvsbds", type=str, help="Remove constant bonded interactions with virtual sites")
@click.option("-maxwarn", type=str, help="Number of allowed warnings during input processing. Not for normal use and may generate unstable systems")
@click.option("-zero", type=str, help="Set parameters for bonded interactions without defaults to zero instead of generating an error")
@click.option("-renum", type=str, help="Renumber atomtypes and minimize number of atomtypes")
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    """Run example.

    Example usage:

    $ gmx_grompp --code gmx@localhost -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_grompp -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Help: $ gmx_grompp --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
