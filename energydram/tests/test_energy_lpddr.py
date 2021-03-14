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

import unittest

import energydram


class TestEnergyDDR(unittest.TestCase):
    '''
    EnergyDDR class unit tests.

    Based on LPDDR3, 8 Gb, x32, dual-die, speed 1600, fast-exit
    (178b_8-16gb_2c0f_mobile_lpddr3.pdf).
    '''

    tck = 1000./800
    timing = energydram.Timing(RRD=10, RAS=42, RP=18, RFC=210, REFI=3900)
    vdd1 = 1.8
    vdd1_lp4 = 1.8
    idds1 = energydram.IDDs(idd0=8, idd2p=0.8, idd2n=0.8, idd3p=1.4,
                            idd3n=2.0, idd4r=2, idd4w=2, idd5=28)
    vdd2 = 1.2
    vdd2_lp4 = 1.1
    idds2 = energydram.IDDs(idd0=60, idd2p=1.8, idd2n=26, idd3p=11,
                            idd3n=34, idd4r=230, idd4w=240, idd5=150)
    vddcaq = 1.2
    vddcaq_lp4 = 1.1
    # NOTE: idd0, idd4r, idd4w, idd5 were 3.
    iddsin = energydram.IDDs(idd0=6, idd2p=0.2, idd2n=6, idd3p=0.2,
                             idd3n=6, idd4r=6, idd4w=6, idd5=6)
    chipcnt = 1

    def test_init(self):
        ''' Initialization. '''
        elpddr3 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=3)
        self.assertEqual(elpddr3.timing, self.timing, 'timing')
        self.assertEqual(elpddr3.vdd1_domain.vdd, self.vdd1, 'vdd1')
        self.assertEqual(elpddr3.vdd2_domain.vdd, self.vdd2, 'vdd2')
        self.assertEqual(elpddr3.vddq_domain.vdd, self.vddcaq, 'vddcaq')
        self.assertEqual(elpddr3.vdd1_domain.idds, self.idds1, 'idds1')
        self.assertEqual(elpddr3.vdd2_domain.idds, self.idds2, 'idds2')
        self.assertEqual(elpddr3.vddq_domain.idds, self.iddsin, 'iddsin')
        for vdom in elpddr3.vdoms:
            self.assertEqual(vdom.tck, self.tck, 'tck')
            self.assertEqual(vdom.chipcnt, self.chipcnt, 'chipcnt')
            self.assertEqual(vdom.burstcycles, 4, 'burstcycles')
        self.assertIn('LPDDR3', elpddr3.type, 'type')

    def test_init_lpddr2(self):
        ''' Initialization for LPDDR2. '''
        elpddr2 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=2)
        self.assertIn('LPDDR2', elpddr2.type, 'type')

    def test_init_lpddr(self):
        ''' Initialize with for LPDDR. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*ddr.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                   self.idds1, self.vdd2, self.idds2,
                                   self.vddcaq, self.iddsin, self.chipcnt,
                                   ddr=1)

    def test_init_lpddr4(self):
        ''' Initialize with for LPDDR4. '''
        elpddr4 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1_lp4,
                                         self.idds1, self.vdd2_lp4, self.idds2,
                                         self.vddcaq_lp4, self.iddsin,
                                         self.chipcnt,
                                         ddr=4)
        self.assertIn('LPDDR4', elpddr4.type, 'type')

    def test_init_lpddr5(self):
        ''' Initialize with for LPDDR5. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*ddr.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                   self.idds1, self.vdd2, self.idds2,
                                   self.vddcaq, self.iddsin, self.chipcnt,
                                   ddr=5)

    def test_init_lpddr23_invalid_vdd1(self):
        ''' Initialize with invalid vdd1 for LPDDR2/3. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vdd1.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, 1.2,
                                   self.idds1, self.vdd2, self.idds2,
                                   self.vddcaq, self.iddsin, self.chipcnt)

    def test_init_lpddr23_invalid_vdd2(self):
        ''' Initialize with invalid vdd2 for LPDDR2/3. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vdd2.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                   self.idds1, 1.8, self.idds2,
                                   self.vddcaq, self.iddsin, self.chipcnt)

    def test_init_lpddr23_invalid_vddcaq(self):  # pylint: disable=invalid-name
        ''' Initialize with invalid vddcaq for LPDDR2/3. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vddcaq.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                   self.idds1, self.vdd2, self.idds2,
                                   1.8, self.iddsin, self.chipcnt)

    def test_init_lpddr23_invalid_timing(self):  # pylint: disable=invalid-name
        ''' Initialize with invalid timing for LPDDR2/3. '''
        with self.assertRaisesRegexp(TypeError, 'EnergyLPDDR: .*timing.*'):
            energydram.EnergyLPDDR(self.tck, None, self.vdd1,
                                   self.idds1, self.vdd2, self.idds2,
                                   self.vddcaq, self.iddsin, self.chipcnt)

    def test_init_lpddr4_invalid_vdd1(self):
        ''' Initialize with invalid vdd1 for LPDDR4. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vdd1.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, 1.2,
                                   self.idds1, self.vdd2_lp4, self.idds2,
                                   self.vddcaq_lp4, self.iddsin, self.chipcnt,
                                   ddr=4)

    def test_init_lpddr4_invalid_vdd2(self):
        ''' Initialize with invalid vdd2 for LPDDR4. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vdd2.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1_lp4,
                                   self.idds1, 1.8, self.idds2,
                                   self.vddcaq_lp4, self.iddsin, self.chipcnt,
                                   ddr=4)

    def test_init_lpddr4_invalid_vddcaq(self):  # pylint: disable=invalid-name
        ''' Initialize with invalid vddcaq for LPDDR4. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyLPDDR: .*vddcaq.*'):
            energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1_lp4,
                                   self.idds1, self.vdd2_lp4, self.idds2,
                                   1.8, self.iddsin, self.chipcnt,
                                   ddr=4)

    def test_background_energy(self):
        ''' Calculate background energy. '''
        elpddr3 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=3)

        pds_pre_lo = elpddr3.background_energy(1, 0, 0, 0) / self.tck
        self.assertIsInstance(pds_pre_lo, float)

        pds_pre_hi = elpddr3.background_energy(0, 1, 0, 0) / self.tck
        self.assertIsInstance(pds_pre_hi, float)

        pds_act_lo = elpddr3.background_energy(0, 0, 1, 0) / self.tck
        self.assertIsInstance(pds_act_lo, float)

        pds_act_hi = elpddr3.background_energy(0, 0, 0, 1) / self.tck
        self.assertIsInstance(pds_act_hi, float)

    def test_activate_energy(self):
        ''' Calculate activate energy. '''
        elpddr3 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=3)

        eact = elpddr3.activate_energy(1)
        pds_act = eact / (self.timing.RAS + self.timing.RP) / self.tck
        self.assertIsInstance(pds_act, float)

    def test_readwrite_energy(self):
        ''' Calculate read/write energy. '''
        elpddr3 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=3)

        erd = elpddr3.readwrite_energy(num_rd=1, num_wr=0)
        pds_rd = erd / 4 / self.tck
        self.assertIsInstance(pds_rd, float)

        ewr = elpddr3.readwrite_energy(num_rd=0, num_wr=1)
        pds_wr = ewr / 4 / self.tck
        self.assertIsInstance(pds_wr, float)

    def test_refresh_energy(self):
        ''' Calculate activate energy. '''
        elpddr3 = energydram.EnergyLPDDR(self.tck, self.timing, self.vdd1,
                                         self.idds1, self.vdd2, self.idds2,
                                         self.vddcaq, self.iddsin, self.chipcnt,
                                         ddr=3)

        eref = elpddr3.refresh_energy(1)
        pds_ref = eref / self.timing.REFI / self.tck
        self.assertIsInstance(pds_ref, float)

