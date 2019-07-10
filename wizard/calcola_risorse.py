# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 CQ creativiquadrati snc
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
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from time import strftime


class calcola_risorse(models.TransientModel):

    _name="calcola.risorse"
    _description="Compute Workload"
    
    year = fields.Selection((('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024')),'Year',required=True)
    reparto_id = fields.Many2one('reparti','Department',required=True)
    
    
    def compute_workload(self):
        
        this=self
        
        start=date(int(this.year),1,1)
        end=date(int(this.year),12,31)        
        #cancello tutti i record riferiti all'anno
        sql="DELETE FROM tabella_risorse WHERE data>='%s' AND data<='%s' AND reparto_id=%s" %(start,end,this.reparto_id.id)
        self.env.cr.execute(sql)

        delta=end-start
        # sarebbe meglio aggiungere una tabella di giorni festivi, per ora sono fissi Natale, vigilia, S.Stefano, capodanno, epifania, 25 aprile, 1 maggio, ferragosto
        festivi=[this.year+'-12-24',this.year+'-12-25',this.year+'-12-26',this.year+'-12-08',this.year+'-01-01',this.year+'-01-06',this.year+'-04-25',this.year+'-05-01',this.year+'-08-15']
        
        for i in range(delta.days +1):
           day= start + timedelta(days=i)
           strday = day.strftime("%Y-%m-%d")
           tab_data={
               'data': day,
               'n_res1': 0,
               'n_res2': 0,
               'n_res3': 0,
               'ore_res1': 0.0,
               'ore_res2': 0.0,
               'ore_res3': 0.0,
               'ore_tot': 0.0,
               'ore_tot_available': 0.0,
               'reparto_id': this.reparto_id.id,
           }
           
           # se non è un festivo o un fine settimana, completa la tabella
           if (strday not in festivi) and (day.weekday()<5):
               risorsa_id=self.env['config.risorse'].search([('inizio','<=',day),('fine','>=',day),('reparto_id','=',this.reparto_id.id)])
               for risorsa in risorsa_id:
               # dovrebbe esserci sempre solo al massimo un record perche controlliamo che non ci siano periodi sovrapposti
                   tab_data['n_res1']=risorsa.n_res1
                   tab_data['n_res2']=risorsa.n_res2
                   tab_data['n_res3']=risorsa.n_res3
                   tab_data['ore_res1']=risorsa.ore_res1
                   tab_data['ore_res2']=risorsa.ore_res2
                   tab_data['ore_res3']=risorsa.ore_res3
                   tab_data['ore_tot']=risorsa.ore_tot               
                   tab_data['ore_tot_available']=risorsa.ore_tot_available
           
           self.env['tabella.risorse'].create(tab_data) 
    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workload Chart',
            'res_model': 'tabella.risorse',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_id': this.id,
        }
    





