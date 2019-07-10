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
import datetime as dt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields,models,api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class mrp_production(models.Model):

    _inherit="mrp.production"
    
    planned_start = fields.Datetime('Planned Start Date')
    planned_end = fields.Datetime('Planned End Date')
    planned_duration = fields.Float('Planned Duration (h)', help='calcolata dalle righe in secondi della diba o (se non ci sono) copiata da tempo pianificato per assemblare')
    reparto_id =fields.Many2one('reparti','Department')
    num_res = fields.Float('Number of resources (actual)')
    actual_duration = fields.Float('Actual Duration (h)', help='per poter inserire a posteriori le durate, fare statistiche e sistemare le durate delle distinte base')
    bloccato = fields.Selection(string='Stato', selection=[('todo', 'Da fare'),('blocco', 'Blocco'),('blcomm', 'Blocco commerciale'),('running', 'In assemblaggio'),('topack', 'Da imballare'),('ready', 'Pronto')])
    prelievo = fields.Selection(string='Prelievo', selection = [('todo', 'Da prelevare'),('done', 'Prelevato')])
    carrello = fields.Char('Codice carrello', size=64)
    note = fields.Text('Note')
    planned_week = fields.Integer(string='Planned week',compute ='_get_planned_week', store=True, readonly=True)
    start_week = fields.Integer(string='Start week',compute ='_get_start_week', store=True, readonly=True)
    # non ho una kanban per settimana, quindi non dovrebbe essere possibile modificare il campo planned_week
    tempo_pian = fields.Float(string='Tempo pianificato per assemblare (h)')   # manuale, usata come default se la diba ha durata 0
    corpo = fields.Char('Corpo', size=16)
    stampata = fields.Selection(string='Stampata', selection=[('S', 'Si'),('N', 'No')])
    contr_ut = fields.Boolean(string='Controllo UT')
    appr_ut = fields.Selection(string='Approvato UT', selection=[('S', 'Approvato UT'),('M', 'Approvato UT con modifiche')])



    @api.model
    def create(self,vals):
        if 'bom_id' in vals:        
            if vals['bom_id']:
                bom=self.env['mrp.bom'].browse(vals['bom_id'])
                if bom:
                    if bom.reparto_id:
                        vals['reparto_id']=bom.reparto_id.id
                    if bom.code:
                        if '-UA-' or '+UA-' in bom.code:
                            vals['corpo'] = 'UA'        
                        elif '-UB-' or '+UB-' in bom.code:
                            vals['corpo'] = 'UB'        
                        elif '-U4-'  or '+U4-' in bom.code:
                            vals['corpo'] = 'U4'        
                        elif '-MR-' or '+MR-' in bom.code:
                            vals['corpo'] = 'MR'
                        elif '-MB-' or '+MB-' in bom.code:
                            vals['corpo'] = 'MB'
                        elif '-M4-' or '+M4-' in bom.code:
                            vals['corpo'] = 'M4'
                        else:
                            vals['corpo'] = 'senza corpo'
                    # compilo per default il tempo medio di assemblaggio
                    compilare = False
                    if not 'tempo_pian' in vals:
                        compilare = True
                    elif vals['tempo_pian'] == 0:
                        compilare = True
                    if compilare:
                        durata=0.0  #inizialmente in secondi
                        for line in bom.bom_line_ids:
                            if not line.product_uom_id or not line.product_uom_id.category_id or (line.product_uom_id.category_id.name<>'Working Time' and line.product_uom_id.category_id.name<>'Orario lavorativo'):
                                continue                
                            if line.product_uom_id.name=='secondi' or line.product_uom_id.name=='s' or line.product_uom_id.name=='sec':
                                durata=durata+line.product_qty*vals['product_qty']   
                            if line.product_uom_id.name=='Hour(s)' or line.product_uom_id.name == 'Ora(e)':
                                durata=durata+line.product_qty*vals['product_qty']*3600            
                            if line.product_uom_id.name=='Day(s)' or line.product_uom_id.name =='Giorno(i)':
                                durata=durata+line.product_qty*vals['product_qty']*86400          
                        # durata totale in ore dell'ordine di produzione se fosse svolto da una persona sola               
                        durata=round(durata/3600., 2)
                        if durata > 0:
                            vals['tempo_pian'] = durata

        res=super(mrp_production, self).create(vals)        
        return res


    @api.multi
    def write(self,vals):   # ??, update=True, mini=True): ??

        for this in self:        
  
            if 'planned_start' in vals:
                # se il tipo è str, vuol dire che sto effettuando delle modifiche da calendario, altrimenti con il wizard pianifica_mo!
                if isinstance(vals['planned_start'],str):
                   new_start=datetime(int(vals['planned_start'][:4]),int(vals['planned_start'][5:7]),int(vals['planned_start'][8:10]),int(vals['planned_start'][11:13]),int(vals['planned_start'][14:16]),int(vals['planned_start'][17:19]))
               

                   duration=this.planned_duration
                   num_giorni=1+duration//8
                   new_end=new_start+relativedelta(hours=duration)
               #if new_end <= datetime(int(vals['planned_start'][:4]),int(vals['planned_start'][5:7]),int(vals['planned_start'][8:10]),16,0,0):
               #    vals['planned_end']=new_end
               
               #else:
               #    avanzo=new_end-datetime(int(vals['planned_start'][:4]),int(vals['planned_start'][5:7]),int(vals['planned_start'][8:10]),16,0,0)
               #    vals['planned_end']=new_start+relativedelta(days=num_giorni)+relativedelta(seconds=avanzo.seconds)
                   vals['planned_end']=new_end
            res=super(mrp_production,self).write(vals)    # ?? ,update,mini)         ??
        
            if not this.reparto_id:
                if this.bom_id:
                    if this.bom_id.reparto_id:
                        sql="UPDATE mrp_production SET reparto_id=%s WHERE id=%s" %(this.bom_id.reparto_id.id, this.id)
                        self.env.cr.execute(sql)        
                    elif this.product_id.categ_id.reparto_id:
                        sql="UPDATE mrp_production SET reparto_id=%s WHERE id=%s" %(this.product_id.categ_id.reparto_id.id, this.id)
                        self.env.cr.execute(sql)        
        
            return res    

    @api.depends('planned_start')
    def _get_planned_week(self):
        for order in self:
            if not order.planned_start:
                order.planned_week = False
                continue
            order_planned_date = order.planned_start.split()[0]  # solo la data senza ora
            delivery_dt = dt.datetime.strptime(order_planned_date, DATE_FORMAT)          
            order.planned_week = delivery_dt.isocalendar()[1] 

    @api.depends('date_planned_start')
    def _get_start_week(self):
        for order in self:
            if not order.date_planned_start:
                order.start_week = False
                continue
            order_start_date = order.date_planned_start.split()[0]  # solo la data senza ora
            delivery_dt = dt.datetime.strptime(order_start_date, DATE_FORMAT)          
            order.start_week = delivery_dt.isocalendar()[1] 



class mrp_bom(models.Model):

    _inherit="mrp.bom"
    
    reparto_id =fields.Many2one('reparti','Department')
 
class ProductCategory(models.Model):

    _inherit="product.category"
    
    reparto_id =fields.Many2one('reparti','Department')
