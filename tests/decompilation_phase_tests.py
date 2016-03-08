#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompilation_phase` module."""

import unittest

from retdec.decompilation_phase import DecompilationPhase


class DecompilationPhaseTests(unittest.TestCase):
    """Tests of :class:`retdec.decompilation_phase.DecompilationPhase`."""

    def test_arguments_passed_to_initializer_are_accessible(self):
        phase = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertEqual(phase.name, 'NAME')
        self.assertEqual(phase.part, 'PART')
        self.assertEqual(phase.description, 'DESCRIPTION')
        self.assertEqual(phase.completion, 75)

    def test_two_phases_with_same_data_are_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertEqual(phase1, phase2)

    def test_two_phases_with_different_name_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='OTHER NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_part_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='OTHER PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_description_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='OTHER DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_completion_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=100
        )

        self.assertNotEqual(phase1, phase2)

    def test_repr_returns_correct_value(self):
        phase = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        self.assertEqual(
            repr(phase),
            ("retdec.decompilation_phase.DecompilationPhase(name='NAME', "
             "part='PART', description='DESCRIPTION', completion=75)")
        )
