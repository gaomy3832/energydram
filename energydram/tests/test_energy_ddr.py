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

    Compare with DDR3_Power_Calc.xlsm.

    Based on DDR3, 2 Gb, x8, -125E, fast-exit.
    '''

    tck = 1000./800
    timing = energydram.Timing(RRD=6, RAS=35, RP=47.5-35, RFC=160, REFI=7800)
    vdd = 1.5
    idds = energydram.IDDs(idd0=95, idd2p=35, idd2n=42, idd3p=40,
                           idd3n=45, idd4r=180, idd4w=185, idd5=215)
    ipps = energydram.IDDs(idd0=3, idd2p=3, idd2n=3, idd3p=3,
                           idd3n=3, idd4r=3, idd4w=3, idd5=3)
    chipcnt = 1

    def test_init(self):
        ''' Initialization. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, self.vdd,
                                     self.idds, self.chipcnt)
        self.assertEqual(eddr3.timing, self.timing, 'timing')
        self.assertEqual(eddr3.vdd_domain.vdd, self.vdd, 'vdd')
        self.assertEqual(eddr3.vdd_domain.idds, self.idds, 'idds')
        for vdom in eddr3.vdoms:
            self.assertEqual(vdom.tck, self.tck, 'tck')
            self.assertEqual(vdom.chipcnt, self.chipcnt, 'chipcnt')
            self.assertEqual(vdom.burstcycles, 4, 'burstcycles')
        self.assertIn('DDR3', eddr3.type, 'type')

    def test_init_ddr2(self):
        ''' Initialization for DDR2. '''
        eddr2 = energydram.EnergyDDR(self.tck, self.timing, 1.8,
                                     self.idds, self.chipcnt, ddr=2)
        self.assertIn('DDR2', eddr2.type, 'type')
        self.assertEqual(eddr2.vdd_domain.burstcycles, 2, 'burstcycles')

    def test_init_ddr3l(self):
        ''' Initialization for DDR3L. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, 1.35,
                                     self.idds, self.chipcnt)
        self.assertIn('DDR3L', eddr3.type, 'type')
        self.assertEqual(eddr3.vdd_domain.burstcycles, 4, 'burstcycles')

    def test_init_ddr4(self):
        ''' Initialize with for DDR4. '''
        eddr4 = energydram.EnergyDDR(self.tck, self.timing, 1.2,
                                     self.idds, self.chipcnt, ddr=4,
                                     vpp=2.5, ipps=self.ipps)
        self.assertIn('DDR4', eddr4.type, 'type')
        self.assertEqual(eddr4.vpp_domain.tck, self.tck, 'tck')
        self.assertEqual(eddr4.vpp_domain.vdd, 2.5, 'vpp')
        self.assertEqual(eddr4.vpp_domain.idds, self.ipps, 'ipps')
        self.assertEqual(eddr4.vpp_domain.chipcnt, self.chipcnt, 'chipcnt')
        self.assertEqual(eddr4.vpp_domain.burstcycles, 4, 'burstcycles')

    def test_init_ddr(self):
        ''' Initialize with for DDR. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*ddr.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.2, self.idds,
                                 self.chipcnt, ddr=1)

    def test_init_ddr5(self):
        ''' Initialize with for DDR5. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*ddr.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.2, self.idds,
                                 self.chipcnt, ddr=5)

    def test_init_ddr2_invalid_vdd(self):
        ''' Initialize with invalid vdd for DDR2. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*vdd.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.2, self.idds,
                                 self.chipcnt, ddr=2)

    def test_init_ddr3_invalid_vdd(self):
        ''' Initialize with invalid vdd for DDR3. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*vdd.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.2, self.idds,
                                 self.chipcnt)

    def test_init_ddr4_invalid_vpp(self):
        ''' Initialize with for DDR4. '''
        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*vdd.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.5,
                                 self.idds, self.chipcnt, ddr=4,
                                 vpp=2.5, ipps=self.ipps)

        with self.assertRaisesRegexp(ValueError, 'EnergyDDR: .*vdd.*'):
            energydram.EnergyDDR(self.tck, self.timing, 1.2,
                                 self.idds, self.chipcnt, ddr=4)

    def test_init_invalid_timing(self):
        ''' Initialize with invalid idds. '''
        with self.assertRaisesRegexp(TypeError, 'EnergyDDR: .*timing.*'):
            energydram.EnergyDDR(self.tck, (1, 2), self.vdd, self.idds,
                                 self.chipcnt)

    def test_background_energy(self):
        ''' Calculate background energy. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, self.vdd,
                                     self.idds, self.chipcnt)

        pds_pre_lo = eddr3.background_energy(1, 0, 0, 0) / self.tck
        self.assertAlmostEqual(pds_pre_lo, 52.5, delta=0.1)

        pds_pre_hi = eddr3.background_energy(0, 1, 0, 0) / self.tck
        self.assertAlmostEqual(pds_pre_hi, 63.0, delta=0.1)

        pds_act_lo = eddr3.background_energy(0, 0, 1, 0) / self.tck
        self.assertAlmostEqual(pds_act_lo, 60.0, delta=0.1)

        pds_act_hi = eddr3.background_energy(0, 0, 0, 1) / self.tck
        self.assertAlmostEqual(pds_act_hi, 67.5, delta=0.1)

    def test_activate_energy(self):
        ''' Calculate activate energy. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, self.vdd,
                                     self.idds, self.chipcnt)

        eact = eddr3.activate_energy(1)
        pds_act = eact / (self.timing.RAS + self.timing.RP) / self.tck
        self.assertAlmostEqual(pds_act, 76.2, delta=0.1)

    def test_readwrite_energy(self):
        ''' Calculate read/write energy. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, self.vdd,
                                     self.idds, self.chipcnt)

        erd = eddr3.readwrite_energy(num_rd=1, num_wr=0)
        pds_rd = erd / 4 / self.tck
        self.assertAlmostEqual(pds_rd, 202.5, delta=0.1)

        ewr = eddr3.readwrite_energy(num_rd=0, num_wr=1)
        pds_wr = ewr / 4 / self.tck
        self.assertAlmostEqual(pds_wr, 210.0, delta=0.1)

    def test_refresh_energy(self):
        ''' Calculate activate energy. '''
        eddr3 = energydram.EnergyDDR(self.tck, self.timing, self.vdd,
                                     self.idds, self.chipcnt)

        eref = eddr3.refresh_energy(1)
        pds_ref = eref / self.timing.REFI / self.tck
        self.assertAlmostEqual(pds_ref, 5.2, delta=0.1)

