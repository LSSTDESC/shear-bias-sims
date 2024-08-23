import logging
import time

import galsim
import numpy as np

from chromatic_weak_lensing import MainSequence

from chromatic_shear_sims import utils


logger = logging.getLogger(__name__)


class StarBuilder:
    def __init__(self, module_name, class_name, **kwargs):
        self.model = utils.get_instance(module_name, class_name, **kwargs)
        self.name = self.model.name

    def __call__(self, stellar_params, **kwargs):
        model_params = self.model.get_params(stellar_params)
        star = self.model.get_star(*model_params, **kwargs)
        return star


class InterpolatedStarBuilder:
    def __init__(self, module_name, class_name, throughput_1, throughput_2, **kwargs):
        self.model = utils.get_instance(module_name, class_name, **kwargs)
        self.name = self.model.name
        self.lut = self.get_lut(throughput_1, throughput_2)
        self.x_min = self.lut.x_min
        self.x_max = self.lut.x_max

    def get_lut(self, throughput_1, throughput_2):
        """
        Get a lookup table so as to find the mass of a star
        whose spectra produces a given color.
        """
        _start_time = time.time()
        logM_min = np.min(MainSequence.logM)
        logM_max = np.max(MainSequence.logM)
        n = 1000
        masses = np.logspace(
            logM_min,
            logM_max,
            n,
        )

        colors = []
        for mass in masses:
            sparams = MainSequence.get_params(mass)
            params = self.model.get_params(sparams)
            spec = self.model.get_spectrum(*params)
            color = spec.calculateMagnitude(throughput_1) - spec.calculateMagnitude(throughput_2)
            colors.append(color)

        lut = galsim.LookupTable(colors, masses, x_log=False, f_log=True, interpolant="linear")
        _end_time = time.time()
        _elapsed_time = _end_time - _start_time
        logger.info(f"made inverse lookup table in {_elapsed_time} seconds")

        return lut

    def get_spec(self, color, **kwargs):
        mass = self.lut(color)
        sparams = MainSequence.get_params(mass)
        params = self.model.get_params(sparams)
        spec = self.model.get_spectrum(*params, **kwargs)
        return spec

    def get_star(self, color, **kwargs):
        mass = self.lut(color)
        sparams = MainSequence.get_params(mass)
        params = self.model.get_params(sparams)
        star = self.model.get_star(*params, **kwargs)
        return star

    def __call__(self, color, **kwargs):
        star = self.get_star(color, **kwargs)
        return star

