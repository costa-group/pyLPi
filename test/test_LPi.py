import unittest
import lpi


class TestKey(unittest.TestCase):
    def test_import(self):
        lpi.C_Polyhedron()
        self.assertEqual(1, 1)

    def test_ppl(self):
        lpi.C_Polyhedron(None,dim=2)
        self.assertEqual(1, 1)
