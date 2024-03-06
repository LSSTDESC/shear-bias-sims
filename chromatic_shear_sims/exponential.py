import functools
import logging
import os
import time

import galsim
import numpy as np
import pyarrow.compute as pc
import pyarrow.dataset as ds


logger = logging.getLogger(__name__)


class ExponentialBlackBodyBuilder:
    def __init__(self, survey):
        from chromatic_shear_sims.blackbody import BlackBody
        logger.info(f"initializing exponential builder with blackbody SEDs")
        self.survey = survey
        self.blackbody = BlackBody(self.survey)

    def make_gal(
         self,
         color,
         half_light_radius,
    ):
        _start_time = time.time()
        gal = galsim.Exponential(half_light_radius=half_light_radius)

        sed = self.blackbody(color)
        sed = sed.withMagnitude(20, self.survey.bandpasses["r"])

        gal = gal * sed


        _end_time = time.time()
        _elapsed_time = _end_time - _start_time
        logger.debug(f"built galaxy in {_elapsed_time} seconds")

        return gal

    def build_gals(
        self,
        n,
        color_min=None,
        color_max=None,
    ):
        # FIXME seed rng
        logger.info(f"building galaxies")
        rng = np.random.default_rng()
        _start_time = time.time()
        gals = []
        for igal in range(n):
            color = rng.uniform(color_min, color_max)
            half_light_radius = 0.5
            gal = self.make_gal(
                color,
                half_light_radius,
            )
            gals.append(gal)

        _end_time = time.time()
        _elapsed_time = _end_time - _start_time
        logger.info(f"built {len(gals)} galaxies in {_elapsed_time} seconds")

        return gals


class ExponentialBlackBodyGalaxies:
    def __init__(self, config, loader, survey=None):
        self.config = config
        self.survey = survey
        self.loader = loader
        self.builder = ExponentialBlackBodyBuilder(survey=self.survey)

        # self.sampling = self.config.get("sampling")
        self.color_min = self.loader.aggregates.get("min_color")
        self.color_max = self.loader.aggregates.get("max_color")


    def __call__(self, n):
        gals = self.builder.build_gals(
            n,
            color_min=self.color_min,
            color_max=self.color_max,
        )
        return gals


if __name__ == "__main__":
    exit()
