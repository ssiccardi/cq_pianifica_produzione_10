# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 CQ creativiquadrati snc
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields,models, api
from odoo.exceptions import UserError, ValidationError

class config_risorse(models.Model):

    _name="config.risorse"
    _description="Workload Management"

  
    inizio = fields.Date('From', required=True)
    fine = fields.Date('To', required=True)
    n_res1 = fields.Integer('Num. resource 1', required=True, default=0)
    n_res2 = fields.Integer('Num. resource 2', required=True, default=0)
    n_res3 = fields.Integer('Num. resource 3', required=True, default=0)
    ore_res1 = fields.Float('Hours/day resource 1', required=True, default=0.0)
    ore_res2 = fields.Float('Hours/day resource 2', required=True, default=0.0)          
    ore_res3 = fields.Float('Hours/day resource 3', required=True, default=0.0)
    ore_tot = fields.Float('Hours/day', required=True,readonly=True, default=0.0)
    ore_tot_available = fields.Float('Hours/day available', required=True, default=0.0)
    reparto_id = fields.Many2one('reparti','Department',required=True)
    


    @api.model
    def create(self,vals):
        if vals['inizio'] >= vals['fine']:
            raise ValidationError("Attenzione! Data di inizio periodo posteriore alla data di fine!")
        
        vals['ore_tot']=vals['n_res1']*vals['ore_res1'] + vals['n_res2']*vals['ore_res2'] + vals['n_res3']*vals['ore_res3']
        vals['ore_tot_available']=vals['ore_tot']
        res=super(config_risorse,self).create(vals)

        other_ids=self.search([('id','!=',res.id),('reparto_id','=',vals['reparto_id'])])
        for other in other_ids:
            #controllo che non ci sia sovrapposizione di periodi
            if (other.inizio>=vals['inizio'] and other.inizio<=vals['fine']) or (other.fine>=vals['inizio'] and other.fine<=vals['fine']) or (other.inizio>=vals['inizio'] and other.fine<=vals['fine']) or (vals['inizio']>=other.inizio and vals['fine']<=other.fine):
                raise ValidationError("Attenzione! Il periodo che stai creando si sovrappone ad un altro per lo stesso reparto!")        
        return res


    @api.multi
    def write(self, vals):   
        
        res=super(config_risorse,self).write(vals)
        #this=self.browse(cr,uid,ids)[0]  this -> self
        for this in self:
            if this.inizio >= this.fine:
                raise ValidationError("Attenzione! Data di inizio periodo posteriore alla data di fine!")
            ore_tot=this.n_res1*this.ore_res1 + this.n_res2*this.ore_res2 + this.n_res3*this.ore_res3
            sql="UPDATE config_risorse SET ore_tot=%s, ore_tot_available=%s WHERE id=%s" %(ore_tot,ore_tot,this.id)
            self.env.cr.execute(sql)
        
            other_ids=self.search([('id','!=',this.id),('reparto_id','=',this.reparto_id.id)])
            for other in other_ids:
                #controllo che non ci sia sovrapposizione di periodi
                if (other.inizio>=this.inizio and other.inizio<=this.fine) or (other.fine>=this.inizio and other.fine<=this.fine) or (other.inizio>=this.inizio and other.fine<=this.fine) or (this.inizio>=other.inizio and this.fine<=other.fine):
                    raise ValidationError("Attenzione! Il periodo che stai creando si sovrappone ad un altro per lo stesso reparto!")        
        return res

    
