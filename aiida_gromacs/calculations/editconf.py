"""
Calculations provided by aiida_gromacs.

This calculation configures the ability to use the 'gmx editconf' executable.
"""
from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import SinglefileData
from aiida.plugins import DataFactory

EditconfParameters = DataFactory("gromacs.editconf")


class EditconfCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the 'gmx editconf' executable.

    AiiDA plugin wrapper for adding a simulation box to structure file.
    """

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super().define(spec)

        # set default values for AiiDA options
        # TODO: something changed about withmpi in aiida-2.4.0, needs investigation.
        spec.inputs['metadata']['options']['withmpi'].default = False
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
        }

        # Requied inputs.
        spec.inputs['metadata']['options']['parser_name'].default = 'gromacs.editconf'
        spec.input('metadata.options.output_filename', valid_type=str, default='editconf.out')
        spec.input('grofile', valid_type=SinglefileData, help='Input structure file.')
        spec.input('parameters', valid_type=EditconfParameters, help='Command line parameters for gmx editconf.')

        # Optional inputs.
        spec.input('n_file', required=False, valid_type=SinglefileData, help='Index file.')
        spec.input('bf_file', required=False, valid_type=SinglefileData, help='Generic data file.')

        # Default outputs.
        spec.output('stdout', valid_type=SinglefileData, help='stdout')
        spec.output('grofile', valid_type=SinglefileData, help='Output file containing simulation box.')

        spec.exit_code(300, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files
            needed by the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        codeinfo = CodeInfo()

        # Setup data structures for files.
        input_options = ["grofile", "n_file", "bf_file"]
        cmdline_input_files = {}
        input_files = []

        # Map input files to AiiDA plugin data types.
        for item in input_options:
            if item in self.inputs:
                cmdline_input_files[item] = self.inputs[item].filename
                input_files.append((
                        self.inputs[item].uuid,
                        self.inputs[item].filename,
                        self.inputs[item].filename,
                    ))

        # Form the commandline.
        codeinfo.cmdline_params = self.inputs.parameters.cmdline_params(cmdline_input_files)

        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = input_files
        calcinfo.retrieve_list = [
            self.metadata.options.output_filename,
            self.inputs.parameters["o"],
        ]

        return calcinfo
