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

from .timing import Timing
from .voltage_domain import VoltageDomain


class EnergyLPDDR(object):
    '''
    Calculate energy for LPDDR2, LPDDR3.
    '''

    def __init__(self, tck, timing, vdd1, idds1, vdd2, idds2, vddcaq, iddsin,
                 chipcnt, ddr=3):
        if ddr == 2 or ddr == 3:
            if round(vdd1, 5) != round(1.8, 5):
                raise ValueError('{}: given vdd1 is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.8 V for LPDDR2/3.')
            if round(vdd2, 5) != round(1.2, 5):
                raise ValueError('{}: given vdd2 is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.2 V for LPDDR2/3.')
            if round(vddcaq, 5) != round(1.2, 5):
                raise ValueError('{}: given vddcaq is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.2 V for LPDDR2/3.')
            self.type = 'LPDDR{}'.format(ddr)
            burstcycles = (1 << ddr) // 2
        elif ddr == 4:
            if round(vdd1, 5) != round(1.8, 5):
                raise ValueError('{}: given vdd1 is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.8 V for LPDDR4.')
            if round(vdd2, 5) != round(1.1, 5):
                raise ValueError('{}: given vdd2 is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.1 V for LPDDR4.')
            if round(vddcaq, 5) != round(1.1, 5):
                raise ValueError('{}: given vddcaq is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.1 V for LPDDR4.')
            self.type = 'LPDDR{}'.format(ddr)
            burstcycles = 4
        elif ddr >= 5:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__)
                             + ' LPDDR5 and above are not supported currently.')
        else:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__))

        if not isinstance(timing, Timing):
            raise TypeError('{}: given timing has invalid type.'
                            .format(self.__class__.__name__))
        self.timing = timing
        self.vdoms = []
        self.vdoms.append(VoltageDomain(tck, vdd1, idds1, chipcnt, burstcycles))
        self.vdoms.append(VoltageDomain(tck, vdd2, idds2, chipcnt, burstcycles))
        self.vdoms.append(VoltageDomain(tck, vddcaq, iddsin, chipcnt, burstcycles))

    def background_energy(self, cycles_bankpre_ckelo=0, cycles_bankpre_ckehi=0,
                          cycles_bankact_ckelo=0, cycles_bankact_ckehi=0):
        ''' Background energy. '''
        return sum(vdom.background_energy(
            cycles_bankpre_ckelo=cycles_bankpre_ckelo,
            cycles_bankpre_ckehi=cycles_bankpre_ckehi,
            cycles_bankact_ckelo=cycles_bankact_ckelo,
            cycles_bankact_ckehi=cycles_bankact_ckehi)
                   for vdom in self.vdoms)

    def activate_energy(self, num_act=1):
        ''' Activate energy. '''
        return sum(vdom.activate_energy(self.timing, num_act=num_act)
                   for vdom in self.vdoms)

    def readwrite_energy(self, num_rd=1, num_wr=0):
        ''' Read write energy. '''
        return sum(vdom.readwrite_energy(num_rd=num_rd, num_wr=num_wr)
                   for vdom in self.vdoms)

    def refresh_energy(self, num_ref=1):
        ''' Refresh energy. '''
        return sum(vdom.refresh_energy(self.timing, num_ref=num_ref)
                   for vdom in self.vdoms)

    @property
    def vdd1_domain(self):
        ''' VDD1 voltage domain. '''
        return self.vdoms[0]

    @property
    def vdd2_domain(self):
        ''' VDD2 voltage domain. '''
        return self.vdoms[1]

    @property
    def vddq_domain(self):
        ''' VDDQ voltage domain. '''
        return self.vdoms[2]

