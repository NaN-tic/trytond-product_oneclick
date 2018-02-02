# This file is part of of product_oneclick module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import product_oneclick


def register():
    Pool.register(
        product_oneclick.ProductOneClickView,
        module='product_oneclick', type_='model')
    Pool.register(
        product_oneclick.ProductOneClick,
        module='product_oneclick', type_='wizard')
