# This file is part of product_oneclick module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval, PYSONEncoder
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.config import CONFIG
DIGITS = int(CONFIG.get('unit_price_digits', 4))

__all__ = ['ProductOneClickView', 'ProductOneClick']


class ProductOneClickView(ModelView):
    'Product OneClick View'
    __name__ = 'product.oneclick.view'
    name = fields.Char('Name', size=None, required=True)
    code = fields.Char('Code', size=None, select=True, required=True)
    description = fields.Text('Description')
    type = fields.Selection([
            ('goods', 'Goods'),
            ('assets', 'Assets'),
            ('service', 'Service')
            ], 'Type', required=True)
    category = fields.Many2One('product.category', 'Category', required=True)
    list_price = fields.Numeric('List Price', digits=(16, DIGITS),
        states={
            'required': Eval('salable', False),
            })
    cost_price = fields.Numeric('Cost Price', digits=(16, DIGITS),
        states={
            'required': Eval('purchasable', False),
            })
    cost_price_method = fields.Selection([
                ("fixed", "Fixed"),
                ("average", "Average")
                ], 'Cost Method', required=True)
    default_uom = fields.Many2One('product.uom', 'Default UOM', required=True)
    default_uom_category = fields.Function(
        fields.Many2One('product.uom.category', 'Default UOM Category'),
        'on_change_with_default_uom_category')
    salable = fields.Boolean('Salable')
    sale_uom = fields.Many2One('product.uom', 'Sale UOM',
        states={
            'invisible':~Eval('salable', False),
            'required': Eval('salable', False),
            },
        #~ domain=[
            #~ ('category', '=', Eval('default_uom_category')),
            #~ ],
        depends=['salable', 'default_uom_category'])
    purchasable = fields.Boolean('Purchasable')
    purchase_uom = fields.Many2One('product.uom', 'Purchase UOM',
        states={
            'invisible':~Eval('purchasable'),
            'required': Eval('purchasable', False),
            },
        #~ domain=[('category', '=', Eval('default_uom_category'))],
        depends=['purchasable', 'default_uom_category'])

    @staticmethod
    def default_type():
        return 'goods'

    @staticmethod
    def default_salable():
        return 1

    @staticmethod
    def default_purchasable():
        return 1

    @staticmethod
    def default_cost_price_method():
        return 'fixed'

    @fields.depends('default_uom', 'sale_uom', 'salable')
    def on_change_with_sale_uom(self):
        Template = Pool().get('product.template')
        template = Template(id=None, default_uom=self.default_uom,
                salable=self.salable, sale_uom=self.sale_uom)
        return template.on_change_with_sale_uom()

    @fields.depends('default_uom', 'purchase_uom', 'purchasable')
    def on_change_with_purchase_uom(self):
        Template = Pool().get('product.template')
        template = Template(id=None, default_uom=self.default_uom,
                purchasable=self.purchasable, purchase_uom=self.purchase_uom)
        return template.on_change_with_purchase_uom()

    @fields.depends('default_uom')
    def on_change_with_default_uom_category(self, name=None):
        Template = Pool().get('product.template')
        template = Template(id=None, default_uom=self.default_uom)
        return template.on_change_with_default_uom_category(name)


class ProductOneClick(Wizard):
    'Product OneClick'
    __name__ = 'product.oneclick'
    start_state = 'view'
    view = StateView('product.oneclick.view',
        'product_oneclick.product_oneclick_view', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_', 'tryton-ok', default=True),
            ])
    create_ = StateTransition()
    open_ = StateAction('product.act_product_form')

    @classmethod
    def __setup__(cls):
        super(ProductOneClick, cls).__setup__()
        cls._error_messages.update({
                'warning': 'Warning',
                'product_exist': 'Product %s (%s) already exist.',
                })

    @classmethod
    def get_template_values(self, vals):
        values = {
            'name': vals.name,
            'type': vals.type,
            'category': vals.category or None,
            'list_price': vals.list_price or 0,
            'cost_price': vals.cost_price or 0,
            'cost_price_method': vals.cost_price_method,
            'default_uom': vals.default_uom,
            'account_category': True,
            }
        if vals.salable:
            values.update({
                'salable': vals.salable,
                'sale_uom': vals.sale_uom,
                })
        if vals.purchasable:
            values.update({
                'purchasable': vals.purchasable,
                'purchase_uom': vals.purchase_uom,
                })
        return values

    @classmethod
    def get_product_values(self, vals):
        values = {
            'code': vals.code,
            'description': vals.description,
            }
        return values

    def transition_create_(self, values=False):
        '''Create a product'''
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        name = self.view.name
        code = self.view.code

        products = None
        if name:
            products = Template.search([('name', '=', name)])
        if code:
            products = Product.search([('code', '=', code)])
        if products:
            self.raise_user_error(error="warning",
                error_description="product_exist",
                error_description_args=(name, code))

        vals = self.view
        tpl_values = self.get_template_values(vals)
        prod_values = self.get_product_values(vals)

        # create template
        self.template = Template.create([tpl_values])[0]
        # create product
        prod_values['template'] = self.template
        self.product = Product.create([prod_values])[0]

        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
                ('id', '=', self.product.id),
                ])
        return action, {}
