#!/usr/local/bin/python2.7
##
# OOIPLACEHOLDER
#
# Copyright 2020 Raytheon Co.
##

import os

from mi.core.versioning import version
from mi.dataset.dataset_driver import SimpleDatasetDriver, ParticleDataHandler
from mi.dataset.dataset_parser import DataSetDriverConfigKeys
from mi.dataset.parser.ctdpf_ckl_wfp import CtdpfCklWfpParser, \
    METADATA_PARTICLE_CLASS_KEY, \
    DATA_PARTICLE_CLASS_KEY
from mi.dataset.parser.wfp_c_file_common import WfpCFileCommonConfigKeys
from mi.dataset.parser.ctdpf_ckl_wfp_particles import \
    CtdpfCklWfpTelemeteredDataParticle, \
    CtdpfCklWfpTelemeteredMetadataParticle, \
    CtdpfCklWfpDataParticleKey

from mi.core.log import get_logger

log = get_logger()


class CtdpfCklWfpDriver(SimpleDatasetDriver):
    """
    Derived wc_wm_cspp driver class
    All this needs to do is create a concrete _build_parser method
    """
    def __init__(self, unused, stream_handle, particle_data_handler, e_file_time_pressure_tuples):
        self._e_file_time_pressure_tuples = e_file_time_pressure_tuples

        super(CtdpfCklWfpDriver, self).__init__(unused, stream_handle, particle_data_handler)

    def _build_parser(self, stream_handle):

        parser_config = {
            WfpCFileCommonConfigKeys.PRESSURE_FIELD_C_FILE: CtdpfCklWfpDataParticleKey.PRESSURE,
            DataSetDriverConfigKeys.PARTICLE_CLASS: None,
            DataSetDriverConfigKeys.PARTICLE_CLASSES_DICT: {
                METADATA_PARTICLE_CLASS_KEY: CtdpfCklWfpTelemeteredMetadataParticle,
                DATA_PARTICLE_CLASS_KEY: CtdpfCklWfpTelemeteredDataParticle
            }
        }

        file_size = os.path.getsize(stream_handle.name)

        parser = CtdpfCklWfpParser(parser_config,
                                   stream_handle,
                                   self._exception_callback,
                                   file_size,
                                   self._e_file_time_pressure_tuples)

        return parser


@version("0.0.1")
def parse(unused, source_file_path, particle_data_handler):
    """
    This is the method called by Uframe
    :param unused
    :param source_file_path This is the full path and filename of the file to be parsed
    :param particle_data_handler Java Object to consume the output of the parser
    :return particle_data_handler
    """

    # Let this be None until we modify the global E file driver to get these tuples
    e_file_time_pressure_tuples = None

    # Parse the ctd file and use the e_file_time_pressure_tuples to generate
    # the internal timestamps of the particles
    with open(source_file_path, 'rb') as stream_handle:
        driver = CtdpfCklWfpDriver(
            unused, stream_handle, particle_data_handler, e_file_time_pressure_tuples)
        driver.processFileStream()

    return particle_data_handler
