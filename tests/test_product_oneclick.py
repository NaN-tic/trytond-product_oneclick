# This file is part of the product_oneclick module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class ProductOneclickTestCase(ModuleTestCase):
    'Test Product Oneclick module'
    module = 'product_oneclick'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductOneclickTestCase))
    return suite