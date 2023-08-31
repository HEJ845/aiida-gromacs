"""
Parsers provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx mdrun' executable.
"""
from aiida.common import exceptions
from aiida.engine import ExitCode
from aiida.orm import SinglefileData
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

MdrunCalculation = CalculationFactory("gromacs.mdrun")


class MdrunParser(Parser):
    """
    Parser class for parsing output of calculation.
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a MdrunCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.nodes.process.process.ProcessNode`
        """
        super().__init__(node)
        if not issubclass(node.process_class, MdrunCalculation):
            raise exceptions.ParsingError("Can only parse MdrunCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: an exit code, if parsing fails (or nothing if parsing succeeds)
        """
        # Map output files to how they are named.
        outputs = ["stdout"]
        output_template = {
                "c": "grofile",
                "e": "enfile",
                "g": "logfile",
                "o": "trrfile",
                "x": "x_file",
                "cpo": "cpo_file",
                "dhdl": "dhdl_file",
                "field": "field_file",
                "tpi": "tpi_file",
                "tpid": "tpid_file",
                "eo": "eo_file",
                "px": "px_file",
                "pf": "pf_file",
                "ro": "ro_file",
                "ra": "ra_file",
                "rs": "rs_file",
                "rt": "rt_file",
                "mtx": "mtx_file",
                "if": "if_file",
                "swap": "swap_file"
            }

        for item in output_template:
            if item in self.node.inputs.parameters.keys():
                outputs.append(output_template[item])

        # Grab list of retrieved files.
        files_retrieved = self.retrieved.base.repository.list_object_names()

        # Grab list of files expected and remove the scheduler stdout and stderr files.
        files_expected = [files for files in self.node.get_option("retrieve_list") if files not in ["_scheduler-stdout.txt", "_scheduler-stderr.txt"]]

        # Check if the expected files are a subset of retrieved.
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(
                f"Found files '{files_retrieved}', expected to find '{files_expected}'"
            )
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # Map retrieved files to data nodes.
        for i, f in enumerate(files_expected):
            self.logger.info(f"Parsing '{f}'")
            with self.retrieved.base.repository.open(f, "rb") as handle:
                output_node = SinglefileData(filename=f, file=handle)
                with open(f, "w") as outfile:
                    outfile.write(output_node.get_content())
            self.out(outputs[i], output_node)

        return ExitCode(0)
