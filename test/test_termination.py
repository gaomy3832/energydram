"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""

import unittest

import energydram


class TestTermResistance(unittest.TestCase):
    ''' TermResistance class unit tests. '''

    def test_init(self):
        ''' Initialization. '''
        resistance = energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                               rtt_wr=120, rtt_mc=75, rs=15)
        self.assertEqual(resistance.rz_dev, 34, 'R_z')
        self.assertEqual(resistance.rz_mc, 34, 'R_zC')
        self.assertEqual(resistance.rtt_nom, 30, 'R_TT,nom')
        self.assertEqual(resistance.rtt_wr, 120, 'R_TT(WR)')
        self.assertEqual(resistance.rtt_mc, 75, 'R_TTC')
        self.assertEqual(resistance.rs, 15, 'R_s')

    def test_init_zero_rz_dev(self):
        ''' Assert rz_dev != 0. '''
        try:
            energydram.TermResistance(rz_dev=0, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('rz_dev', str(e))
            return
        self.fail()

    def test_init_negative_rz_dev(self):
        ''' Assert rz_dev > 0. '''
        try:
            energydram.TermResistance(rz_dev=-10, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('rz_dev', str(e))
            return
        self.fail()

    def test_init_zero_rz_mc(self):
        ''' Assert rz_mc != 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=0, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('rz_mc', str(e))
            return
        self.fail()

    def test_init_negative_rz_mc(self):
        ''' Assert rz_mc > 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=-10, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('rz_mc', str(e))
            return
        self.fail()

    def test_init_zero_rtt_nom(self):
        ''' Assert rtt_nom != 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=0,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('R_TT,nom', str(e))
            return
        self.fail()

    def test_init_negative_rtt_nom(self):
        ''' Assert rtt_nom > 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=-10,
                                      rtt_wr=120, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('R_TT,nom', str(e))
            return
        self.fail()

    def test_init_zero_rtt_wr(self):
        ''' Assert rtt_wr != 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=0, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('R_TT(WR)', str(e))
            return
        self.fail()

    def test_init_negative_rtt_wr(self):
        ''' Assert rtt_wr > 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=-10, rtt_mc=75, rs=15)
        except ValueError as e:
            self.assertIn('R_TT(WR)', str(e))
            return
        self.fail()

    def test_init_zero_rtt_mc(self):
        ''' Assert rtt_mc != 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=0, rs=15)
        except ValueError as e:
            self.assertIn('rtt_mc', str(e))
            return
        self.fail()

    def test_init_negative_rtt_mc(self):
        ''' Assert rtt_mc > 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=-10, rs=15)
        except ValueError as e:
            self.assertIn('rtt_mc', str(e))
            return
        self.fail()

    def test_init_zero_rs(self):
        ''' Assert rs != 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=0)
        except ValueError as e:
            self.assertIn('rs', str(e))
            return
        self.fail()

    def test_init_negative_rs(self):
        ''' Assert rs > 0. '''
        try:
            energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=30,
                                      rtt_wr=120, rtt_mc=75, rs=-10)
        except ValueError as e:
            self.assertIn('rs', str(e))
            return
        self.fail()


class TestTermination(unittest.TestCase):
    '''
    Termination class unit tests.

    Compare with DDR3_Power_Calc.xlsm, default setting but Rs1 = 15 for write.
    '''

    vdd = 1.5
    rankcnt = 2
    resistance = energydram.TermResistance(rz_dev=34, rz_mc=34, rtt_nom=40,
                                           rtt_wr=30, rtt_mc=60, rs=15)

    def test_init(self):
        ''' Initialization. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertEqual(term.vdd, self.vdd, 'vdd')
        self.assertEqual(term.rankcnt, self.rankcnt, 'rankcnt')
        self.assertEqual(term.resistance, self.resistance, 'resistance')

    def test_init_invalid_vdd(self):
        ''' Initialize with invalid vdd. '''
        try:
            energydram.Termination(-1.2, self.rankcnt, self.resistance)
        except ValueError as e:
            self.assertIn('vdd', str(e))
            return
        self.fail()

    def test_init_invalid_rankcnt(self):
        ''' Initialize with invalid rankcnt. '''
        try:
            energydram.Termination(self.vdd, 1.2, self.resistance)
        except TypeError as e:
            self.assertIn('rankcnt', str(e))
            try:
                energydram.Termination(self.vdd, 0, self.resistance)
            except ValueError as e:
                self.assertIn('rankcnt', str(e))
                return
            self.fail()
        self.fail()

    def test_init_invalid_resistance(self):
        ''' Initialize with invalid resistance. '''
        try:
            energydram.Termination(self.vdd, self.rankcnt, None)
        except TypeError as e:
            self.assertIn('resistance', str(e))
            return
        self.fail()

    def test_power_total(self):
        ''' Assert total power is the sum of mem controller and devices. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertAlmostEqual(
            term.read_power_total(),
            term.read_power_memctlr() + term.read_power_devices(),
            places=6)
        self.assertAlmostEqual(
            term.write_power_total(),
            term.write_power_memctlr() + term.write_power_devices(),
            places=6)

    def test_power_devices(self):
        ''' Assert DRAM device power is the sum of all ranks. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertAlmostEqual(
            term.read_power_devices(),
            term.read_power_target_rank() + term.read_power_other_ranks(),
            places=6)
        self.assertAlmostEqual(
            term.write_power_devices(),
            term.write_power_target_rank() + term.write_power_other_ranks(),
            places=6)

    def test_power_memctlr(self):
        ''' Calculate memory controller power. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertAlmostEqual(term.read_power_memctlr(), 10.7e-3,
                               places=4)
        self.assertAlmostEqual(term.write_power_memctlr(), 5.5e-3,
                               places=4)

    def test_power_target_rank(self):
        ''' Calculate DRAM device power at the target rank. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertAlmostEqual(term.read_power_target_rank(), 3.2e-3 + 1.4e-3,
                               places=4)
        self.assertAlmostEqual(term.write_power_target_rank(), 20.2e-3 + .74e-3,
                               places=4)

    def test_power_other_ranks(self):
        ''' Calculate DRAM device power at other ranks. '''
        term = energydram.Termination(self.vdd, self.rankcnt, self.resistance)
        self.assertAlmostEqual(term.read_power_other_ranks(), 15e-3 + 0.48e-3,
                               places=4)
        self.assertAlmostEqual(term.write_power_other_ranks(), 15.4e-3 + 0.5e-3,
                               places=4)


if __name__ == '__main__':
    unittest.main()
