from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
from datetime import timedelta,datetime

_logger = logging.getLogger(__name__)

class salesorder(models.Model):
    _inherit = 'purchase.order'
    

class stock_move(models.Model):
    _inherit='stock.move'
    @api.constrains('state')
    def get_state(self):
        stock_move=self.env['stock.move'].search([])
        """for stock in stock_move :
            if self.origin:
                sale_order=self.env['sale.order'].search([('name','=',stock.origin)])
                purchase_order=self.env['purchase.order'].search([('name','=',stock.origin)])
                if sale_order:
                    stock.date=sale_order.date_order
                if purchase_order:
                    stock.date=purchase_order.date_order"""
        for rec in self:
          if rec.origin:
            sale_order=self.env['sale.order'].search([('name','=',rec.origin)])
            purchase_order=self.env['purchase.order'].search([('name','=',rec.origin)])
            _logger.info("LEngtht")
            _logger.info(len(sale_order))
            
            if sale_order:
                
                
               
                rec.date=sale_order.date_order
            if purchase_order:
                rec.date=purchase_order.date_order
            
            
                   


