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
        elif ddr >= 4:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__)
                             + ' LPDDR4 and above are not supported currently.')
        else:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__))

        if not isinstance(timing, Timing):
            raise TypeError('{}: given timing has invalid type.'
                            .format(self.__class__.__name__))
        self.timing = timing
        self.vdom1 = VoltageDomain(tck, vdd1, idds1, chipcnt, ddr=ddr)
        self.vdom2 = VoltageDomain(tck, vdd2, idds2, chipcnt, ddr=ddr)
        self.vdomcaq = VoltageDomain(tck, vddcaq, iddsin, chipcnt, ddr=ddr)

    def background_energy(self, cycles_bankpre_ckelo=0, cycles_bankpre_ckehi=0,
                          cycles_bankact_ckelo=0, cycles_bankact_ckehi=0):
        ''' Background energy. '''
        return self.vdom1.background_energy(
            cycles_bankpre_ckelo=cycles_bankpre_ckelo,
            cycles_bankpre_ckehi=cycles_bankpre_ckehi,
            cycles_bankact_ckelo=cycles_bankact_ckelo,
            cycles_bankact_ckehi=cycles_bankact_ckehi) \
        + self.vdom2.background_energy(
            cycles_bankpre_ckelo=cycles_bankpre_ckelo,
            cycles_bankpre_ckehi=cycles_bankpre_ckehi,
            cycles_bankact_ckelo=cycles_bankact_ckelo,
            cycles_bankact_ckehi=cycles_bankact_ckehi) \
        + self.vdomcaq.background_energy(
            cycles_bankpre_ckelo=cycles_bankpre_ckelo,
            cycles_bankpre_ckehi=cycles_bankpre_ckehi,
            cycles_bankact_ckelo=cycles_bankact_ckelo,
            cycles_bankact_ckehi=cycles_bankact_ckehi)

    def activate_energy(self, num_act=1):
        ''' Activate energy. '''
        return self.vdom1.activate_energy(self.timing, num_act=num_act) \
                + self.vdom2.activate_energy(self.timing, num_act=num_act) \
                + self.vdomcaq.activate_energy(self.timing, num_act=num_act)

    def readwrite_energy(self, num_rd=1, num_wr=0):
        ''' Read write energy. '''
        return self.vdom1.readwrite_energy(num_rd=num_rd, num_wr=num_wr) \
                + self.vdom2.readwrite_energy(num_rd=num_rd, num_wr=num_wr) \
                + self.vdomcaq.readwrite_energy(num_rd=num_rd, num_wr=num_wr)

    def refresh_energy(self, num_ref=1):
        ''' Refresh energy. '''
        return self.vdom1.refresh_energy(self.timing, num_ref=num_ref) \
                + self.vdom2.refresh_energy(self.timing, num_ref=num_ref) \
                + self.vdomcaq.refresh_energy(self.timing, num_ref=num_ref)

