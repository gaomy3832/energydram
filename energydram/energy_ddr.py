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


class EnergyDDR(object):
    '''
    Calculate energy for DDR2, DDR3(L).
    '''

    def __init__(self, tck, timing, vdd, idds, chipcnt, ddr=3,
                 vpp=None, ipps=None):
        if ddr == 2:
            if round(vdd, 5) != round(1.8, 5):
                raise ValueError('{}: given vdd is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.8 V for DDR2.')
            self.type = 'DDR2'
            burstcycles = 2
        elif ddr == 3:
            if round(vdd, 5) == round(1.5, 5):
                self.type = 'DDR3'
                burstcycles = 4
            elif round(vdd, 5) == round(1.35, 5):
                self.type = 'DDR3L'
                burstcycles = 4
            else:
                raise ValueError('{}: given vdd is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.5 V for DDR3, '
                                 'or 1.35 V for DDR3L.')
        elif ddr == 4:
            if not (vpp is None and ipps is None) and \
                    round(vdd, 5) == round(1.2, 5) and \
                    round(vpp, 5) == round(2.5, 5):
                self.type = 'DDR4'
                burstcycles = 4
            else:
                raise ValueError('{}: given vdd or vpp is invalid.'
                                 .format(self.__class__.__name__)
                                 + ' should be 1.2 V and 2.5 V for DDR4.')
        elif ddr >= 5:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__)
                             + ' DDR5 and above are not supported currently.')
        else:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__))

        if not isinstance(timing, Timing):
            raise TypeError('{}: given timing has invalid type.'
                            .format(self.__class__.__name__))
        self.timing = timing
        self.vdoms = []
        self.vdoms.append(VoltageDomain(tck, vdd, idds, chipcnt, burstcycles))
        if ddr >= 4:
            self.vdoms.append(VoltageDomain(tck, vpp, ipps, chipcnt, burstcycles))

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
    def vdd_domain(self):
        ''' VDD voltage domain. '''
        return self.vdoms[0]

    @property
    def vpp_domain(self):
        ''' VPP voltage domain. '''
        return self.vdoms[1]

