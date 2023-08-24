#!/usr/bin/env python
"""Launch a calculation using the 'general-MD'

This script allows the user to submit via AiiDA any command of a code that 
is set up in AiiDA

"""

import os
from pathlib import Path
import click

from aiida import cmdline, engine, orm, load_profile
from aiida.common import exceptions
from aiida.plugins import CalculationFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious

# set base path for input files.
INPUT_DIR = os.path.join(os.getcwd())
profile = load_profile()
computer = helpers.get_computer()
code = helpers.get_code(entry_point="gromacs", computer=computer)
code = helpers.get_code(entry_point="bash", computer=computer)


def launch_generalMD(options):
    """Run general-MD"""

    code = options["code"]
    command = options["command"]
    inputs = options["inputs"]
    outputs = options["outputs"]
    output_dir = options["output_dir"]

    print(f"command: {command}")

    if not code:
        raise exceptions.NonExistent("Code has not been set.")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # MyAppCalculation = CalculationFactory("general-MD")

    # Check if a previous calculation with the same input parameter
    # value has been stored by loading the QueryBuilder and append
    # all previous jobs ordered by newest first.
    qb = searchprevious.build_query()
    # qb.append(MyAppCalculation, tag="calcjob")
    # qb.order_by({MyAppCalculation: {"ctime": "desc"}})

    # Wait for previous process to finish if running
    searchprevious.check_prev_process(qb)

    # Save list of input files to a dict with keys that are formatted
    # file names and values that are SinglefileData.
    input_files = {}
    for filename in list(inputs):
        file_path = os.path.join(INPUT_DIR, filename)
        stripped_input = filename.split("/")[-1]
        input_files[searchprevious.format_link_label(stripped_input)] = \
            orm.SinglefileData(file=file_path)

    # Keep the output filenames as a list.
    output_files = list(outputs)

    # create input dictionary for calculation.
    process_inputs = {
        "code": code,
        "command": orm.Str(command),
        "input_files": input_files,
        "output_files": orm.List(output_files),
        "metadata": {
            "label": "general-execute",
            "description": "Run CLI job and save input and output file provenance.",
            "options": {
                "output_filename": "file.out",
                "output_dir": output_dir,
                "parser_name": "general-MD",
            },
        },
    }

    # check if previous processes have run and add previous outputs
    # as inputs for new process if file names match
    if qb.count() > 0:
        process_inputs = searchprevious.append_prev_nodes(qb, inputs, 
                        process_inputs, INPUT_DIR)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Submit your calculation to the aiida daemon
    # pylint: disable=unused-variable
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("general-MD"), 
                               **process_inputs)
    else:
        future = engine.submit(CalculationFactory("general-MD"), 
                               **process_inputs)
    # future = engine.submit(process)
    print(f"Submitted calculation: {future}\n")


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
@click.option(
    "--command",
    type=str,
    help="The full command used to run the job enclosed in quotes.",
)
@click.option(
    "--inputs",
    type=str,
    multiple=True,
    help="Input file name used in the command. "
    "Include the local path to these files.",
)
@click.option(
    "--outputs", multiple=True, type=str, 
    help="Output file name used in the command."
)
@click.option(
    "--output_dir",
    default=os.path.join(os.getcwd()) + "/outputs",
    type=str,
    help="Absolute path of directory where files are saved.",
)
def cli(**kwargs):
    """Run generalMD for use with general commands outside of gromacs

    Example usage for equivalent of running gmx_pdb2gmx:

    $ ./generalMD.py --code gmx@localhost
    --command "pdb2gmx -i 1AKI_restraints.itp -o 1AKI_forcfield.gro
    -p 1AKI_topology.top -ff oplsaa -water spce -f 1AKI_clean.pdb"
    --inputs 1AKI_clean.pdb
    --outputs 1AKI_restraints.itp
    --outputs 1AKI_topology.top
    --outputs 1AKI_forcefield.gro

    Help: $ ./generalMD.py --help
    """
    launch_generalMD(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
