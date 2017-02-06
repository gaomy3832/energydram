"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
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

    def __init__(self, vdd, rankcnt, resistance, rdpincnt=1, wrpincnt=1):
        '''
        As an example to specify pin count, for a x8 device, read pin count
        includes 8 DQ and 2 DQS, a total of 10; write pin count also includes
        a datamask, a total of 11. See TN-41-01.
        '''
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
        if not isinstance(rdpincnt, int):
            raise TypeError('{}: given rdpincnt has invalid type.'
                            .format(self.__class__.__name__))
        if rdpincnt <= 0:
            raise ValueError('{}: given rdpincnt is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(wrpincnt, int):
            raise TypeError('{}: given wrpincnt has invalid type.'
                            .format(self.__class__.__name__))
        if wrpincnt <= 0:
            raise ValueError('{}: given wrpincnt is invalid.'
                             .format(self.__class__.__name__))

        self.vdd = vdd
        self.rankcnt = rankcnt
        self.resistance = resistance
        self.rdpincnt = rdpincnt
        self.wrpincnt = wrpincnt

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
        # V0/rz_dev + (V0 - VMC)/rs = 0
        coef[0, 0] = 1. / rz_dev + 1. / rs
        coef[0, rankcnt] = -1. / rs
        rhs[0] = 0
        # Other rankcnt: rtt_nom, 2x up to VDD and down to GND.
        # (Vi - VDD)/2rtt_nom + Vi/2rtt_nom + (Vi - VMC)/rs = 0
        for idx in range(1, rankcnt):
            coef[idx, idx] = 1. / rtt_nom + 1. / rs
            coef[idx, rankcnt] = -1. / rs
            rhs[idx] = vdd * 1. / 2 / rtt_nom
        # MC: rtt_mc, 2x up to VDD and down to GND.
        # (VMC - VDD)/2rtt_mc + VMC/2rtt_mc + sum (VMC - Vi)/rs = 0
        for jdx in range(rankcnt):
            coef[rankcnt, jdx] = -1. / rs
        coef[rankcnt, rankcnt] = 1. / rtt_mc + rankcnt * 1. / rs
        rhs[rankcnt] = vdd * 1. / 2 / rtt_mc

        rd_vnodes = np.linalg.solve(coef, rhs)

        self.rd_power = np.zeros(rankcnt + 1)
        self.rd_power[0] = \
                (rd_vnodes[0] ** 2) / rz_dev \
                + ((rd_vnodes[0] - rd_vnodes[-1]) ** 2) / rs
        for idx in range(1, rankcnt):
            self.rd_power[idx] = \
                    ((rd_vnodes[idx] - vdd) ** 2) / 2 / rtt_nom \
                    + (rd_vnodes[idx] ** 2) / 2 / rtt_nom \
                    + ((rd_vnodes[idx] - rd_vnodes[-1]) ** 2) / rs
        self.rd_power[-1] = \
                ((rd_vnodes[-1] - vdd) ** 2) / 2 / rtt_mc \
                + (rd_vnodes[-1] ** 2) / 2 / rtt_mc

        # DRAM write.

        coef = np.zeros((rankcnt + 1, rankcnt + 1))
        rhs = np.zeros(rankcnt + 1)
        # Rank 0: rtt_wr, 2x up to VDD and down to GND.
        # (V0 - VDD)/2rtt_wr + V0/2rtt_wr + (V0 - VMC)/rs = 0
        coef[0, 0] = 1. / rtt_wr + 1. / rs
        coef[0, rankcnt] = -1. / rs
        rhs[0] = vdd * 1. / 2 / rtt_wr
        # Other rankcnt: rtt_nom, 2x up to VDD and down to GND.
        # (Vi - VDD)/2rtt_nom + Vi/2rtt_nom + (Vi - VMC)/rs = 0
        for idx in range(1, rankcnt):
            coef[idx, idx] = 1. / rtt_nom + 1. / rs
            coef[idx, rankcnt] = -1. / rs
            rhs[idx] = vdd * 1. / 2 / rtt_nom
        # MC: rz_mc, to GND.
        # VMC/rz_mc + sum (VMC - Vi)/rs = 0
        for jdx in range(rankcnt):
            coef[rankcnt, jdx] = -1. / rs
        coef[rankcnt, rankcnt] = 1. / rz_mc + rankcnt * 1. / rs
        rhs[rankcnt] = 0

        wr_vnodes = np.linalg.solve(coef, rhs)

        self.wr_power = np.zeros(rankcnt + 1)
        self.wr_power[0] = \
                ((wr_vnodes[0] - vdd) ** 2) / 2 / rtt_wr \
                + (wr_vnodes[0] ** 2) / 2 / rtt_wr \
                + ((wr_vnodes[0] - wr_vnodes[-1]) ** 2) / rs
        for idx in range(1, rankcnt):
            self.wr_power[idx] = \
                    ((wr_vnodes[idx] - vdd) ** 2) / 2 / rtt_nom \
                    + (wr_vnodes[idx] ** 2) / 2 / rtt_nom \
                    + ((wr_vnodes[idx] - wr_vnodes[-1]) ** 2) / rs
        self.wr_power[-1] = (wr_vnodes[-1] ** 2) / rz_mc

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

