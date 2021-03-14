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

_IDDsBase = namedtuple('_IDDsBase', ['idd0', 'idd2n', 'idd2p', 'idd3n',
                                     'idd3p', 'idd4r', 'idd4w', 'idd5'])

class IDDs(_IDDsBase):
    '''
    Define the set of IDD values.
    '''

    def __new__(cls, **kwargs):
        # http://stackoverflow.com/a/3624799
        self = super(IDDs, cls).__new__(cls, **kwargs)
        self.check()
        return self

    def check(self):
        ''' Check validation of IDD values. '''
        if self.idd2n < self.idd2p:
            raise ValueError('{}: IDD2N < IDD2P!'
                             .format(self.__class__.__name__))
        if self.idd3n < self.idd3p:
            raise ValueError('{}: IDD3N < IDD3P!'
                             .format(self.__class__.__name__))
        if self.idd3n < self.idd2n:
            raise ValueError('{}: IDD3N < IDD2N!'
                             .format(self.__class__.__name__))
        if self.idd3p < self.idd2p:
            raise ValueError('{}: IDD3P < IDD2P!'
                             .format(self.__class__.__name__))
        if self.idd0 < self.idd3n:
            raise ValueError('{}: IDD0 < IDD3N!'
                             .format(self.__class__.__name__))
        if self.idd4r < self.idd3n:
            raise ValueError('{}: IDD4R < IDD3N!'
                             .format(self.__class__.__name__))
        if self.idd4w < self.idd3n:
            raise ValueError('{}: IDD4W < IDD3N!'
                             .format(self.__class__.__name__))
        if self.idd5 < self.idd3n:
            raise ValueError('{}: IDD5 < IDD3N!'
                             .format(self.__class__.__name__))


class VoltageDomain(object):
    '''
    Define a voltage domain including VDD and IDD values.
    '''

    def __init__(self, tck, vdd, idds, chipcnt, burstcycles):
        if tck < 0:
            raise ValueError('{}: given tck is invalid.'
                             .format(self.__class__.__name__))
        if vdd < 0:
            raise ValueError('{}: given vdd is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(idds, IDDs):
            raise TypeError('{}: given idds has invalid type.'
                            .format(self.__class__.__name__))
        if not isinstance(chipcnt, int):
            raise TypeError('{}: given chipcnt has invalid type.'
                            .format(self.__class__.__name__))
        if chipcnt <= 0:
            raise ValueError('{}: given chipcnt is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(burstcycles, int):
            raise TypeError('{}: given burstcycles has invalid type.'
                            .format(self.__class__.__name__))
        if burstcycles <= 0:
            raise ValueError('{}: given burstcycles is invalid.'
                             .format(self.__class__.__name__))
        self.tck = tck
        self.vdd = vdd
        self.idds = idds
        self.chipcnt = chipcnt
        self.burstcycles = burstcycles

    def background_energy(self, cycles_bankpre_ckelo=0, cycles_bankpre_ckehi=0,
                          cycles_bankact_ckelo=0, cycles_bankact_ckehi=0):
        ''' Background energy. '''
        chipicyc = (self.idds.idd2p * cycles_bankpre_ckelo
                    + self.idds.idd2n * cycles_bankpre_ckehi
                    + self.idds.idd3p * cycles_bankact_ckelo
                    + self.idds.idd3n * cycles_bankact_ckehi)
        return chipicyc * self.vdd * self.tck * self.chipcnt

    def activate_energy(self, timing, num_act=1):
        ''' Activate energy. '''
        cycles_rc = (timing.RAS + timing.RP)
        chipicyc = num_act * (self.idds.idd0 * cycles_rc
                              - self.idds.idd3n * timing.RAS
                              - self.idds.idd2n * (cycles_rc - timing.RAS))
        return chipicyc * self.vdd * self.tck * self.chipcnt

    def readwrite_energy(self, num_rd=1, num_wr=0):
        ''' Read write energy. '''
        chipicyc = self.burstcycles * (
            (self.idds.idd4r - self.idds.idd3n) * num_rd
            + (self.idds.idd4w - self.idds.idd3n) * num_wr)
        return chipicyc * self.vdd * self.tck * self.chipcnt

    def refresh_energy(self, timing, num_ref=1):
        ''' Refresh energy. '''
        chipicyc = timing.RFC * (self.idds.idd5 - self.idds.idd3n) * num_ref
        return chipicyc * self.vdd * self.tck * self.chipcnt

