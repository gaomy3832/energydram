"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
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

    def __init__(self, tck, vdd, idds, chipcnt, ddr=3):
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
        if not isinstance(ddr, int):
            raise TypeError('{}: given ddr has invalid type.'
                            .format(self.__class__.__name__))
        if ddr < 0:
            raise ValueError('{}: given ddr is invalid.'
                             .format(self.__class__.__name__))
        self.tck = tck
        self.vdd = vdd
        self.idds = idds
        self.chipcnt = chipcnt
        self.ddr = ddr

    def background_energy(self, cycles_bankpre_ckelo, cycles_bankpre_ckehi,
                          cycles_bankact_ckelo, cycles_bankact_ckehi):
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

    def readwrite_energy(self, num_rd=1, num_wr=1):
        ''' Read write energy. '''
        cyc_burst = (1 << self.ddr) / 2 if self.ddr >= 1 else 1
        chipicyc = cyc_burst * ((self.idds.idd4r - self.idds.idd3n) * num_rd
                                + (self.idds.idd4w - self.idds.idd3n) * num_wr)
        return chipicyc * self.vdd * self.tck * self.chipcnt

    def refresh_energy(self, timing, num_ref=1):
        ''' Refresh energy. '''
        chipicyc = timing.RFC * (self.idds.idd5 - self.idds.idd3n) * num_ref
        return chipicyc * self.vdd * self.tck * self.chipcnt

