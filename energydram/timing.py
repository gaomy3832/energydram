"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""

from collections import namedtuple

# Alphabetical order.
_TIMING_PARAM_LIST = [
    'RAS',
    'REFI',
    'RFC',
    'RP',
    'RRD',
    ]

'''
Define timing parameters in unit of cycles.
'''
Timing = namedtuple('Timing', _TIMING_PARAM_LIST)

