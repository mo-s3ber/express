from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)
class char_account_custom(models.Model):
    _inherit = "account.account"
    check=fields.Boolean('check',default=False)
    @api.onchange('parent_id')
    def get_code(self):
        _logger.info('Codeeeeeeee')
         
        _logger.info(self.parent_id.code)
        #_logger.info(self.parent_id.child_ids.code)
        
        list_code=[]
        if self.parent_id:
            
            for rec in self.parent_id.child_ids:
                list_code.append(int(rec.code))
            list_code=sorted(list_code)
            _logger.info(self.parent_id.child_ids)
            _logger.info(list_code)
            last_code=str(list_code[len(list_code)-1])
            last_code=last_code[len(last_code)-3:]
            _logger.info(last_code)
            _logger.info((int(last_code)))
        
            if self.parent_id:
                if (int(last_code)+1)<999:
                    if int(last_code)==0:
                        self.code=str(self.parent_id.code)+'001'
                    else:
                        _logger.info(len(last_code))
                        if int(last_code)<100:
                            _logger.info('small')
                            self.code=str(self.parent_id.code)+"00"+str(int(last_code)+1)

                        else:
                            self.code=str(self.parent_id.code)+str(int(last_code)+1)
                    self.check=True


                else:
                    self.check=False
                    raise ValidationError('Error Code')

           