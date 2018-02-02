# This file is part of product_oneclick module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.product_oneclick.tests.test_product_oneclick import suite
except ImportError:
    from .test_product_oneclick import suite

__all__ = ['suite']
