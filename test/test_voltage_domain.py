"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""

import unittest

import energydram


class TestIDDs(unittest.TestCase):
    ''' IDDs class unit tests. '''
    def test_init(self):
        ''' Initialization. '''
        idds = energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=45,
                               idd3n=75, idd4r=220, idd4w=240, idd5=255)
        self.assertEqual(idds.idd0, 115, 'IDD0')
        self.assertEqual(idds.idd2p, 25, 'IDD2P')
        self.assertEqual(idds.idd2n, 65, 'IDD2N')
        self.assertEqual(idds.idd3p, 45, 'IDD3P')
        self.assertEqual(idds.idd3n, 75, 'IDD3N')
        self.assertEqual(idds.idd4r, 220, 'IDD4R')
        self.assertEqual(idds.idd4w, 240, 'IDD4W')
        self.assertEqual(idds.idd5, 255, 'IDD5')

    def test_init_2n_vs_2p(self):
        ''' Assert IDD2N >= IDD2P. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=15, idd3p=45,
                            idd3n=75, idd4r=220, idd4w=240, idd5=255)
        except ValueError as e:
            self.assertIn('2N', str(e))
            self.assertIn('2P', str(e))
            return
        self.fail()

    def test_init_3n_vs_3p(self):
        ''' Assert IDD3N >= IDD3P. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=95,
                            idd3n=75, idd4r=220, idd4w=240, idd5=255)
        except ValueError as e:
            self.assertIn('3N', str(e))
            self.assertIn('3P', str(e))
            return
        self.fail()

    def test_init_3n_vs_2n(self):
        ''' Assert IDD3N >= IDD2N. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=45,
                            idd3n=55, idd4r=220, idd4w=240, idd5=255)
        except ValueError as e:
            self.assertIn('3N', str(e))
            self.assertIn('2N', str(e))
            return
        self.fail()

    def test_init_3p_vs_2p(self):
        ''' Assert IDD3P >= IDD2P. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=15,
                            idd3n=75, idd4r=220, idd4w=240, idd5=255)
        except ValueError as e:
            self.assertIn('3P', str(e))
            self.assertIn('2P', str(e))
            return
        self.fail()

    def test_init_4r_vs_3n(self):
        ''' Assert IDD4R >= IDD3N. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=45,
                            idd3n=75, idd4r=70, idd4w=240, idd5=255)
        except ValueError as e:
            self.assertIn('4R', str(e))
            self.assertIn('3N', str(e))
            return
        self.fail()

    def test_init_4w_vs_3n(self):
        ''' Assert IDD4W >= IDD3N. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=45,
                            idd3n=75, idd4r=220, idd4w=70, idd5=255)
        except ValueError as e:
            self.assertIn('4W', str(e))
            self.assertIn('3N', str(e))
            return
        self.fail()

    def test_init_5_vs_3n(self):
        ''' Assert IDD5 >= IDD3N. '''
        try:
            energydram.IDDs(idd0=115, idd2p=25, idd2n=65, idd3p=45,
                            idd3n=75, idd4r=220, idd4w=240, idd5=70)
        except ValueError as e:
            self.assertIn('5', str(e))
            self.assertIn('3N', str(e))
            return
        self.fail()


class TestVoltageDomain(unittest.TestCase):
    '''
    VoltageDomain class unit tests.

    Compare with DDR3_Power_Calc.xlsm.

    Based on DDR3, 2 Gb, x8, -125E, fast-exit.
    '''

    tck = 1000./800
    vdd = 1.575
    idds = energydram.IDDs(idd0=95, idd2p=35, idd2n=42, idd3p=40,
                           idd3n=45, idd4r=180, idd4w=185, idd5=215)
    chipcnt = 1
    timing = energydram.Timing(RAS=35, RP=47.5-35, RFC=160, REFI=7800)

    def test_init(self):
        ''' Initialization. '''
        vdom = energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                        self.chipcnt)
        self.assertEqual(vdom.tck, self.tck, 'tck')
        self.assertEqual(vdom.vdd, self.vdd, 'vdd')
        self.assertEqual(vdom.idds, self.idds, 'idds')
        self.assertEqual(vdom.chipcnt, self.chipcnt, 'chipcnt')
        self.assertEqual(vdom.ddr, 3, 'ddr')

    def test_init_invalid_tck(self):
        ''' Initialize with invalid tck. '''
        try:
            energydram.VoltageDomain(-1, self.vdd, self.idds, self.chipcnt)
        except ValueError as e:
            self.assertIn('tck', str(e))
            return
        self.fail()

    def test_init_invalid_vdd(self):
        ''' Initialize with invalid vdd. '''
        try:
            energydram.VoltageDomain(self.tck, -1.2, self.idds, self.chipcnt)
        except ValueError as e:
            self.assertIn('vdd', str(e))
            return
        self.fail()

    def test_init_invalid_idds(self):
        ''' Initialize with invalid idds. '''
        try:
            energydram.VoltageDomain(self.tck, self.vdd, None, self.chipcnt)
        except TypeError as e:
            self.assertIn('idds', str(e))
            return
        self.fail()

    def test_init_invalid_chipcnt(self):
        ''' Initialize with invalid chipcnt. '''
        try:
            energydram.VoltageDomain(self.tck, self.vdd, self.idds, None)
        except TypeError as e:
            self.assertIn('chipcnt', str(e))
            try:
                energydram.VoltageDomain(self.tck, self.vdd, self.idds, 0)
            except ValueError as e:
                self.assertIn('chipcnt', str(e))
                return
            self.fail()
        self.fail()

    def test_init_invalid_ddr(self):
        ''' Initialize with invalid ddr. '''
        try:
            energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                     self.chipcnt, 0.5)
        except TypeError as e:
            self.assertIn('ddr', str(e))
            try:
                energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                         self.chipcnt, -1)
            except ValueError as e:
                self.assertIn('ddr', str(e))
                return
            self.fail()
        self.fail()

    def test_background_energy(self):
        ''' Calculate background energy. '''
        vdom = energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                        self.chipcnt, ddr=3)

        pds_pre_lo = vdom.background_energy(1, 0, 0, 0) / vdom.tck
        self.assertAlmostEqual(pds_pre_lo, 55.1, delta=0.1)

        pds_pre_hi = vdom.background_energy(0, 1, 0, 0) / vdom.tck
        self.assertAlmostEqual(pds_pre_hi, 66.2, delta=0.1)

        pds_act_lo = vdom.background_energy(0, 0, 1, 0) / vdom.tck
        self.assertAlmostEqual(pds_act_lo, 63.0, delta=0.1)

        pds_act_hi = vdom.background_energy(0, 0, 0, 1) / vdom.tck
        self.assertAlmostEqual(pds_act_hi, 70.9, delta=0.1)

    def test_activate_energy(self):
        ''' Calculate activate energy. '''
        vdom = energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                        self.chipcnt, ddr=3)

        eact = vdom.activate_energy(self.timing, 1)
        pds_act = eact / (self.timing.RAS + self.timing.RP) / vdom.tck
        self.assertAlmostEqual(pds_act, 80.0, delta=0.1)

    def test_readwrite_energy(self):
        ''' Calculate read/write energy. '''
        vdom = energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                        self.chipcnt, ddr=3)

        erd = vdom.readwrite_energy(num_rd=1, num_wr=0)
        pds_rd = erd / 4 / vdom.tck
        self.assertAlmostEqual(pds_rd, 212.6, delta=0.1)

        ewr = vdom.readwrite_energy(num_rd=0, num_wr=1)
        pds_wr = ewr / 4 / vdom.tck
        self.assertAlmostEqual(pds_wr, 220.5, delta=0.1)

    def test_refresh_energy(self):
        ''' Calculate activate energy. '''
        vdom = energydram.VoltageDomain(self.tck, self.vdd, self.idds,
                                        self.chipcnt, ddr=3)

        eref = vdom.refresh_energy(self.timing, 1)
        pds_ref = eref / self.timing.REFI / vdom.tck
        self.assertAlmostEqual(pds_ref, 5.5, delta=0.1)


if __name__ == '__main__':
    unittest.main()

