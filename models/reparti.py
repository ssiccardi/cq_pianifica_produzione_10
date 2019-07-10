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

from odoo import fields,models,api

class reparti(models.Model):

    _name="reparti"
    _description="Reparti di produzione"


    name = fields.Char('Name', required=True)
    
    _order = "name"


class tabella_risorse(models.Model):
    _name="tabella.risorse"
    _description="Workload"


    data = fields.Date('Date', required=True)
    n_res1 = fields.Integer('Num. resource 1', required=True, default=0)
    n_res2 = fields.Integer('Num. resource 2', required=True, default=0)
    n_res3 = fields.Integer('Num. resource 3', required=True, default=0)
    ore_res1 = fields.Float('Hours/day resource 1', required=True, default=0.0)
    ore_res2 = fields.Float('Hours/day resource 2', required=True, default=0.0)          
    ore_res3 = fields.Float('Hours/day resource 3', required=True, default=0.0)
    ore_tot = fields.Float('Hours/day', required=True,readonly=True, default=0.0)
    ore_tot_available = fields.Float('Available Hours/day',required=True, default=0.0)
    reparto_id = fields.Many2one('reparti','Department', required=True)
    num_ordini = fields.Integer('Number of orders starting today', required=True, default=0)    


    @api.model
    def create(self,vals):        
        vals['ore_tot_available']=vals['ore_tot']   
        res=super(tabella_risorse,self).create(vals)   
        return res


    @api.multi
    def write(self,vals):        

        res=super(tabella_risorse,self).write(vals)
        #this=self.browse(cr,uid,ids)[0]
        for this in self:
            ore_tot=this.n_res1*this.ore_res1 + this.n_res2*this.ore_res2 + this.n_res3*this.ore_res3
            sql="UPDATE tabella_risorse SET ore_tot=%s, ore_tot_available=%s WHERE id=%s" %(ore_tot,ore_tot,this.id)
        self.env.cr.execute(sql) 
       
        return res
