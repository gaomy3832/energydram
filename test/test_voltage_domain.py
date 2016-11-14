"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""

import unittest

import energydram


class IDDsDomain(unittest.TestCase):
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
    ''' VoltageDomain class unit tests. '''

    tck = 1000./533
    vdd = 1.5
    idds = energydram.IDDs(idd0=140, idd2p=25, idd2n=65, idd3p=45,
                           idd3n=80, idd4r=280, idd4w=350, idd5=255)
    chipcnt = 1

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


if __name__ == '__main__':
    unittest.main()

