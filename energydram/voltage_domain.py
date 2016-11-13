"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""

from collections import namedtuple

IDDs = namedtuple('IDDs', ['idd0', 'idd2n', 'idd2p', 'idd3n', 'idd3p', 'idd4r',
                           'idd4w', 'idd5'])

def _check_idds(idds):
    ''' Check validation of IDD values. '''
    return idds.idd2n >= idds.idd2p \
            and idds.idd3n >= idds.idd3p \
            and idds.idd3n >= idds.idd2n \
            and idds.idd3p >= idds.idd2p


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
        if _check_idds(idds):
            raise ValueError('{}: given idds is invalid.'
                             .format(self.__class__.__name__))
        if not isinstance(chipcnt, int):
            raise TypeError('{}: given chipcnt has invalid type.'
                            .format(self.__class__.__name__))
        if not isinstance(ddr, int):
            raise TypeError('{}: given ddr has invalid type.'
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

