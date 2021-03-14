""" $lic$
Copyright (c) 2016-2021, Mingyu Gao
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

from collections import namedtuple
import numpy as np

_TermResistanceBase = namedtuple('_TermResistanceBase',
                                 ['rz_dev', 'rz_mc', 'rtt_nom', 'rtt_wr',
                                  'rtt_mc', 'rs'])

class TermResistance(_TermResistanceBase):
    '''
    Define the set of termination resistance values.

    rz_dev: DRAM device output driver impedance.
    rz_mc: memory controller output driver impedance.
    rtt_nom: nominal termination.
    rtt_wr: dynamic write termination.
    rtt_mc: memory controller termination.
    rs: trace impedance.
    '''

    def __new__(cls, **kwargs):
        # http://stackoverflow.com/a/3624799
        self = super(TermResistance, cls).__new__(cls, **kwargs)
        self.check()
        return self

    def check(self):
        ''' Check validation of termination resistance values. '''
        if self.rz_dev < 1e-4:
            raise ValueError('{}: given device driver impedance rz_dev '
                             'is invalid.'
                             .format(self.__class__.__name__))
        if self.rz_mc < 1e-4:
            raise ValueError('{}: given memory ctlr driver impedance rz_mc '
                             'is invalid.'
                             .format(self.__class__.__name__))
        if self.rtt_nom < 1e-4:
            raise ValueError('{}: given device R_TT,nom is invalid.'
                             .format(self.__class__.__name__))
        if self.rtt_wr < 1e-4:
            raise ValueError('{}: given device R_TT(WR) is invalid.'
                             .format(self.__class__.__name__))
        if self.rtt_mc < 1e-4:
            raise ValueError('{}: given memory ctlr termination rtt_mc '
                             'is invalid.'
                             .format(self.__class__.__name__))
        if self.rs < 1e-4:
            raise ValueError('{}: given trace impedance rs is invalid.'
                             .format(self.__class__.__name__))


class Termination(object):
    '''
    Termination scheme for an individual chip.
    '''

    def __init__(self, vdd, rankcnt, resistance, width=0, level='mid',
                 with_dqs=True, with_dm=True, with_dbi=False):
        '''
        `width` specifies the chip width and determines the pin count
        associated to termination. Currently support 0, 4, 8, 16, 32. Valid for
        DDR2, DDR3, DDR4, LPDDR3, LPDDR4, and GDDR5.

        Should be configured with `with_dqs`, `with_dm`, `with_dbi` to specify
        the presence of DQS, DM, DBI pins.

        DDR2/3/4 and LPDDR3 have DQS and DM but no DBI.

        GDDR5 does not have DQS or DM, but has DBI.

        LPDDR4 has DQS and DMI (which is dual-use DM and DBI).

        A special value 0 for `width` means to calculate for a single pin.

        `level` can be 'high', 'low', or 'mid'. DDR2 and DDR3 use mid; DDR4
        uses high; LPDDR4 uses low.

        high: single R_TT connects to VDD.

        low: single R_TT connects to GND.

        mid: R_TTU connects to VDD and R_TTD connects to GND, both are 2 * R_TT.
        '''
        # pylint: disable=too-many-branches

        if vdd < 0:
            raise ValueError('{}: given vdd is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(rankcnt, int):
            raise TypeError('{}: given rankcnt has invalid type.'
                            .format(self.__class__.__name__))
        if rankcnt <= 0:
            raise ValueError('{}: given rankcnt is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(resistance, TermResistance):
            raise TypeError('{}: given resistance has invalid type.'
                            .format(self.__class__.__name__))

        self.vdd = vdd
        self.rankcnt = rankcnt
        self.resistance = resistance

        if width == 0:
            self.rdpincnt = 1
            self.wrpincnt = 1
        elif width >= 4 and ((width & (width - 1)) == 0):
            # Width must be power of 2.

            self.rdpincnt = 0
            self.wrpincnt = 0
            # DQ switch is halved, DBI for each eight-pin group.
            if with_dbi:
                self.rdpincnt += width / 2 + max(1, width / 8)
                self.wrpincnt += width / 2 + max(1, width / 8)
            else:
                self.rdpincnt += width
                self.wrpincnt += width
            # DQS, DQS# for each eight-pin group.
            self.rdpincnt += (max(1, width / 8) * 2 if with_dqs else 0)
            self.wrpincnt += (max(1, width / 8) * 2 if with_dqs else 0)
            # DM for each eight-pin group.
            self.wrpincnt += (max(1, width / 8) if with_dm else 0)
        else:
            raise ValueError('{}: given width is invalid.'
                             .format(self.__class__.__name__))

        if level == 'high':
            vdd_eq = vdd / 1.
            v_drv = 0.
        elif level == 'low':
            vdd_eq = 0.
            v_drv = vdd / 1.
        elif level == 'mid':
            vdd_eq = vdd / 2.
            v_drv = 0.
        else:
            raise ValueError('{}: given level is invalid.'
                             .format(self.__class__.__name__))

        rz_dev = resistance.rz_dev
        rz_mc = resistance.rz_mc
        rtt_nom = resistance.rtt_nom
        rtt_wr = resistance.rtt_wr
        rtt_mc = resistance.rtt_mc
        rs = resistance.rs

        # According to nodal-voltage analysis, solve coef * vnodes = rhs, where
        # vnodes = [V0, V1, V2, ..., VMC], for DRAM read and DRAM write,
        # respectively.

        # DRAM read.

        coef = np.zeros((rankcnt + 1, rankcnt + 1))
        rhs = np.zeros(rankcnt + 1)
        # Rank 0: rz_dev, to GND.
        # (V0 - Vdrv)/rz_dev + (V0 - VMC)/rs = 0
        coef[0, 0] = 1. / rz_dev + 1. / rs
        coef[0, rankcnt] = -1. / rs
        rhs[0] = v_drv / rz_dev
        # Other rankcnt: rtt_nom, 2x up to VDD and down to GND.
        # (Vi - VDD)/2rtt_nom + Vi/2rtt_nom + (Vi - VMC)/rs = 0
        for idx in range(1, rankcnt):
            coef[idx, idx] = 1. / rtt_nom + 1. / rs
            coef[idx, rankcnt] = -1. / rs
            rhs[idx] = vdd_eq / rtt_nom
        # MC: rtt_mc, 2x up to VDD and down to GND.
        # (VMC - VDD)/2rtt_mc + VMC/2rtt_mc + sum (VMC - Vi)/rs = 0
        coef[rankcnt, 0:rankcnt] = -1. / rs
        coef[rankcnt, rankcnt] = 1. / rtt_mc + rankcnt * 1. / rs
        rhs[rankcnt] = vdd_eq / rtt_mc

        rd_vnodes = np.linalg.solve(coef, rhs)

        self.rd_power = np.zeros(rankcnt + 1)
        self.rd_power[0] = \
                ((rd_vnodes[0] - v_drv) ** 2) / rz_dev \
                + ((rd_vnodes[0] - rd_vnodes[-1]) ** 2) / rs
        for idx in range(1, rankcnt):
            if level == 'mid':
                self.rd_power[idx] = \
                        ((rd_vnodes[idx] - vdd) ** 2) / 2 / rtt_nom \
                        + (rd_vnodes[idx] ** 2) / 2 / rtt_nom \
                        + ((rd_vnodes[idx] - rd_vnodes[-1]) ** 2) / rs
            elif level == 'high':
                self.rd_power[idx] = \
                        ((rd_vnodes[idx] - vdd) ** 2) / rtt_nom \
                        + ((rd_vnodes[idx] - rd_vnodes[-1]) ** 2) / rs
            elif level == 'low':
                self.rd_power[idx] = \
                        ((rd_vnodes[idx]) ** 2) / rtt_nom \
                        + ((rd_vnodes[idx] - rd_vnodes[-1]) ** 2) / rs
        if level == 'mid':
            self.rd_power[-1] = \
                    ((rd_vnodes[-1] - vdd) ** 2) / 2 / rtt_mc \
                    + (rd_vnodes[-1] ** 2) / 2 / rtt_mc
        elif level == 'high':
            self.rd_power[-1] = ((rd_vnodes[-1] - vdd) ** 2) / rtt_mc
        elif level == 'low':
            self.rd_power[-1] = ((rd_vnodes[-1]) ** 2) / rtt_mc

        # DRAM write.

        coef = np.zeros((rankcnt + 1, rankcnt + 1))
        rhs = np.zeros(rankcnt + 1)
        # Rank 0: rtt_wr, 2x up to VDD and down to GND.
        # (V0 - VDD)/2rtt_wr + V0/2rtt_wr + (V0 - VMC)/rs = 0
        coef[0, 0] = 1. / rtt_wr + 1. / rs
        coef[0, rankcnt] = -1. / rs
        rhs[0] = vdd_eq / rtt_wr
        # Other rankcnt: rtt_nom, 2x up to VDD and down to GND.
        # (Vi - VDD)/2rtt_nom + Vi/2rtt_nom + (Vi - VMC)/rs = 0
        for idx in range(1, rankcnt):
            coef[idx, idx] = 1. / rtt_nom + 1. / rs
            coef[idx, rankcnt] = -1. / rs
            rhs[idx] = vdd_eq / rtt_nom
        # MC: rz_mc, to GND.
        # (VMC - Vdrv)/rz_mc + sum (VMC - Vi)/rs = 0
        coef[rankcnt, 0:rankcnt] = -1. / rs
        coef[rankcnt, rankcnt] = 1. / rz_mc + rankcnt * 1. / rs
        rhs[rankcnt] = v_drv / rz_mc

        wr_vnodes = np.linalg.solve(coef, rhs)

        self.wr_power = np.zeros(rankcnt + 1)
        if level == 'mid':
            self.wr_power[0] = \
                    ((wr_vnodes[0] - vdd) ** 2) / 2 / rtt_wr \
                    + (wr_vnodes[0] ** 2) / 2 / rtt_wr \
                    + ((wr_vnodes[0] - wr_vnodes[-1]) ** 2) / rs
        elif level == 'high':
            self.wr_power[0] = \
                    ((wr_vnodes[0] - vdd) ** 2) / rtt_wr \
                    + ((wr_vnodes[0] - wr_vnodes[-1]) ** 2) / rs
        elif level == 'low':
            self.wr_power[0] = \
                    ((wr_vnodes[0]) ** 2) / rtt_wr \
                    + ((wr_vnodes[0] - wr_vnodes[-1]) ** 2) / rs
        for idx in range(1, rankcnt):
            if level == 'mid':
                self.wr_power[idx] = \
                        ((wr_vnodes[idx] - vdd) ** 2) / 2 / rtt_nom \
                        + (wr_vnodes[idx] ** 2) / 2 / rtt_nom \
                        + ((wr_vnodes[idx] - wr_vnodes[-1]) ** 2) / rs
            elif level == 'high':
                self.wr_power[idx] = \
                        ((wr_vnodes[idx] - vdd) ** 2) / rtt_nom \
                        + ((wr_vnodes[idx] - wr_vnodes[-1]) ** 2) / rs
            elif level == 'low':
                self.wr_power[idx] = \
                        ((wr_vnodes[idx]) ** 2) / rtt_nom \
                        + ((wr_vnodes[idx] - wr_vnodes[-1]) ** 2) / rs
        self.wr_power[-1] = ((wr_vnodes[-1] - v_drv) ** 2) / rz_mc

        # Multiply pin count to be a whole chip.
        self.rd_power *= self.rdpincnt
        self.wr_power *= self.wrpincnt

    def read_power_total(self):
        ''' Get DRAM read termination power. '''
        return self.rd_power.sum()

    def write_power_total(self):
        ''' Get DRAM write termination power. '''
        return self.wr_power.sum()

    def read_power_memctlr(self):
        ''' Get DRAM read termination power at memory controller. '''
        return self.rd_power[-1]

    def write_power_memctlr(self):
        ''' Get DRAM write termination power at memory controller. '''
        return self.wr_power[-1]

    def read_power_devices(self):
        ''' Get DRAM read termination power at DRAM devices. '''
        return self.rd_power[:self.rankcnt].sum()

    def write_power_devices(self):
        ''' Get DRAM write termination power at DRAM devices. '''
        return self.wr_power[:self.rankcnt].sum()

    def read_power_target_rank(self):
        ''' Get DRAM read termination power at the target rank. '''
        return self.rd_power[0]

    def write_power_target_rank(self):
        ''' Get DRAM write termination power at the target rank. '''
        return self.wr_power[0]

    def read_power_other_ranks(self):
        ''' Get DRAM read termination power at other ranks. '''
        return self.rd_power[1:self.rankcnt].sum() if self.rankcnt > 1 else 0

    def write_power_other_ranks(self):
        ''' Get DRAM write termination power at other ranks. '''
        return self.wr_power[1:self.rankcnt].sum() if self.rankcnt > 1 else 0

