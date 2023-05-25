#!/usr/bin/env python
"""CLI utility to run gmx pdb2gmx with AiiDA.

Usage: gmx_pdb2gmx --help
"""

import os

import click

from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers


def launch(params):
    """Run pdb2gmx.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # If code is not initialised, then setup.
    gromacs_code = params.pop("code")
    if not gromacs_code:
        computer = helpers.get_computer()
        gromacs_code = helpers.get_code(entry_point="gromacs", computer=computer)

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    pdbfile = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))

    Pdb2gmxParameters = DataFactory("gromacs.pdb2gmx")
    parameters = Pdb2gmxParameters(params)

    # set up calculation
    inputs = {
        "code": gromacs_code,
        "parameters": parameters,
        "pdbfile": pdbfile,
        "metadata": {
            "description": "record pdb2gmx data provenance via the aiida_gromacs plugin",
        },
    }

    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    future = engine.submit(CalculationFactory("gromacs.pdb2gmx"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Input file options
@click.option("-f", default="conf.gro", type=str, help="Input structure file")
# Output file options 
@click.option("-o", default="out.gro", type=str, help="Output structure file")
@click.option("-p", default="out.gro", type=str, help="Output topology file")
@click.option("-i", default="out.gro", type=str, help="Output itp file")
@click.option("-n", default="out.gro", type=str, help="Output index file")
@click.option("-q", default="out.gro", type=str, help="Output Structure file")
# Parameter options
@click.option("-chainsep", type=str, help="Condition in PDB files when a new chain should be started (adding termini): id_or_ter, id_and_ter, ter, id, interactive")
@click.option("-merge", type=str, help="Merge multiple chains into a single [moleculetype]: no, all, interactive")
@click.option("-ff", required=True, type=str, help="Forcefield")
@click.option("-water", required=True, type=str, help="Water model")

@click.option("-inter", type=str, help="Set the next 8 options to interactive")
@click.option("-ss", type=str, help="Interactive SS bridge selection")
@click.option("-ter", type=str, help="Interactive termini selection, instead of charged (default)")
@click.option("-lys", type=str, help="Interactive lysine selection, instead of charged")
@click.option("-arg", type=str, help="Interactive arginine selection, instead of charged")
@click.option("-asp", type=str, help="Interactive aspartic acid selection, instead of charged")
@click.option("-glu", type=str, help="Interactive glutamic acid selection, instead of charged")
@click.option("-gln", type=str, help="Interactive glutamine selection, instead of charged")
@click.option("-his", type=str, help="Interactive histidine selection, instead of checking H-bonds")
@click.option("-angle", type=str, help="Minimum hydrogen-donor-acceptor angle for a H-bond (degrees)")
@click.option("-dist", type=str, help="Maximum donor-acceptor distance for a H-bond (nm)")
@click.option("-una", type=str, help="Select aromatic rings with united CH atoms on phenylalanine, tryptophane and tyrosine")
@click.option("-ignh", type=str, help="Ignore hydrogen atoms that are in the coordinate file")
@click.option("-missing", type=str, help="Continue when atoms are missing and bonds cannot be made, dangerous")
@click.option("-v", type=str, help="Force constant for position restraints")
@click.option("-posrefc", type=str, help="Force constant for position restraints")
@click.option("-vsite", type=str, help="Convert atoms to virtual sites: none, hydrogens, aromatics")
@click.option("-heavyh", type=str, help="Make hydrogen atoms heavy")
@click.option("-deuterate", type=str, help="Change the mass of hydrogens to 2 amu")
@click.option("-chargegrp", type=str, help="Use charge groups in the .rtp file")
@click.option("-cmap", type=str, help="Use cmap torsions (if enabled in the .rtp file)")
@click.option("-renum", type=str, help="Renumber the residues consecutively in the output")
@click.option("-rtpres", type=str, help="Use .rtp entry names as residue names")
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    # pylint: disable=line-too-long
    """Run example.

    Example usage:

    $ gmx_pdb2gmx --code gmx@localhost -f 1AKI_clean.pdb -ff oplsaa -water spce -o 1AKI_forcefield.gro -p 1AKI_topology.top -i 1AKI_restraints.itp

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_pdb2gmx -f 1AKI_clean.pdb -ff oplsaa -water spce -o 1AKI_forcefield.gro -p 1AKI_topology.top -i 1AKI_restraints.itp

    Help: $ gmx_pdb2gmx --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
