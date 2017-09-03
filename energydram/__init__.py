""" $lic$
Copyright (c) 2016-2017, Mingyu Gao
All rights reserved.

This program is free software: you can redistribute it and/or modify it under
the terms of the Modified BSD-3 License as published by the Open Source
Initiative.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the BSD-3 License for more details.

You should have received a copy of the Modified BSD-3 License along with this
program. If not, see <https://opensource.org/licenses/BSD-3-Clause>.
"""

from .energy_ddr import EnergyDDR
from .energy_lpddr import EnergyLPDDR
from .termination import TermResistance, Termination
from .timing import Timing
from .voltage_domain import IDDs, VoltageDomain

__version__ = '0.3.0'

