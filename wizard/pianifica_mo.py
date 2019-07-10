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


class pianifica_mo(models.TransientModel):

    _name="pianifica.mo"
    _description="Manufacturing Order planning"
    
    inizializzazione = fields.Date('Inizialization Date',required=True, default=fields.Date.today)
    reparto_id = fields.Many2one('reparti', 'Department', required=True)


    def plan_mo(self):
        
        mrp_pool=self.env['mrp.production']
        # aggiorno i reparti default sugli MO che non lo hanno, prendendolo dalla categoria del prodotto
        mrp_norep = mrp_pool.search([('state','not in',('done','progress','cancel')),('reparto_id','=',False)])
        for produzione in mrp_norep:
            if produzione.product_id.categ_id.reparto_id:
                if not produzione.bom_id.reparto_id:
                    produzione.bom_id.reparto_id = produzione.product_id.categ_id.reparto_id
                produzione.write({'reparto_id': produzione.bom_id.reparto_id.id})

        for this in self:
        
            risorse_pool=self.env['tabella.risorse']
            #prende tutti gli MO del reparto scelto non completati, in ordine di data, e li rischedula a partire da quello con data più vecchia
            mrp_ids=mrp_pool.search([('state','not in',('done','progress','cancel')),('reparto_id','=',this.reparto_id.id)],order='date_planned_start')
            
            inizio=datetime(int(this.inizializzazione[:4]),int(this.inizializzazione[5:7]),int(this.inizializzazione[8:10]),8,0,0)
            inizio_day=this.inizializzazione
            ore_produzione=8.0
    
            festivi_ids=risorse_pool.search([])
            festivi_array=[]
            for festivo in festivi_ids:
                if festivo.ore_tot == 0.0:
                    festivi_array.append(festivo.data)
         
        
            #count_order=0
        
            for mrp in mrp_ids:
    
                mrp_data={}            
                inizio_ordine=False
               
                #calcola durata
                if not mrp.bom_id or mrp.bom_id.type<>'normal':
                    continue
                
                durata=0.0  #inizialmente in secondi
                for line in mrp.bom_id.bom_line_ids:
                    if not line.product_uom_id or not line.product_uom_id.category_id or (line.product_uom_id.category_id.name<>'Working Time' and line.product_uom_id.category_id.name<>'Orario lavorativo'):
                        continue                
                    if line.product_uom_id.name=='secondi' or line.product_uom_id.name=='s' or line.product_uom_id.name=='sec':
                        durata=durata+line.product_qty*mrp.product_qty   
                    if line.product_uom_id.name=='Hour(s)' or line.product_uom_id.name == 'Ora(e)':
                        durata=durata+line.product_qty*mrp.product_qty*3600            
                    if line.product_uom_id.name=='Day(s)' or line.product_uom_id.name =='Giorno(i)':
                        durata=durata+line.product_qty*mrp.product_qty*86400
            
                # durata totale in ore dell'ordine di produzione se fosse svolto da una persona sola               
                durata=durata/3600.
                if durata == 0:
                    durata = mrp.tempo_pian   
                mrp_data['planned_duration']=durata

                for i in range(10000):
                    day = datetime.strptime(inizio_day,'%Y-%m-%d') + timedelta(days=i)
                    day = datetime.strftime(day,'%Y-%m-%d')
                    day_hs = inizio + timedelta(days=i)                
                    ris_id = risorse_pool.search([('data','=',day),('reparto_id','=',this.reparto_id.id)])
                    if not ris_id:
                        continue
                    ris = ris_id[0]
                    if ris.ore_tot_available == 0.0:
                        continue
                

                    if ris.ore_tot_available >= durata:
                        new_ore_available=ris.ore_tot_available-durata                                       
                        #sql="UPDATE tabella_risorse SET ore_tot_available=%s WHERE id=%s" %(new_ore_available,ris.id)
                        #self.env.cr.execute(sql)
                        ris.ore_tot_available = new_ore_available
                        durata_normalizzata=8*durata/ris.ore_tot
                        nuovo_inizio = day_hs +relativedelta(hours=durata_normalizzata)                    
                        if not inizio_ordine:
                        
                            ##conta il numero di ordini che già iniziano in quel giorno                        
                            data=datetime(day_hs.year,day_hs.month,day_hs.day,8,0,0)
                            data_str=datetime.strftime(data,'%Y-%m-%d %H:%M:%S')                       
                            sql2="SELECT num_ordini FROM tabella_risorse WHERE data='%s' AND reparto_id=%s"%(data_str,this.reparto_id.id)                 
                            self.env.cr.execute(sql2)
                            cont=self.env.cr.fetchone()
                            cont=cont[0]                                          
                            mrp_data['planned_start']=datetime(day_hs.year,day_hs.month,day_hs.day,8,0,0) + relativedelta(minutes=cont)                        
                            #sql3="UPDATE tabella_risorse SET num_ordini=num_ordini+1 WHERE data='%s' AND reparto_id=%s"%(data_str,this.reparto_id.id)
                            #self.env.cr.execute(sql3)      
                            ris.num_ordini = ris.num_ordini + 1                
                            inizio_ordine=True
                        mrp_data['planned_end']=datetime(day_hs.year,day_hs.month,day_hs.day,16,0,0)                
                        #self.env.cr.commit()
                        break
                     
                    else:
                        nuova_durata = durata - ris.ore_tot_available   #ore che sono avanzate
                        durata=nuova_durata
                        if not inizio_ordine:
                        
                            ##conta il numero di ordini che già iniziano in quel giorno                        
                            data=datetime(day_hs.year,day_hs.month,day_hs.day,8,0,0)
                            data_str=datetime.strftime(data,'%Y-%m-%d %H:%M:%S')                        
                            sql2="SELECT num_ordini FROM tabella_risorse WHERE data='%s' AND reparto_id=%s"%(data_str,this.reparto_id.id)                        
                            self.env.cr.execute(sql2)
                            cont=self.env.cr.fetchone()
                            cont=cont[0]                                          
                            mrp_data['planned_start']=datetime(day_hs.year,day_hs.month,day_hs.day,8,0,0) + relativedelta(minutes=cont)                        
                            #sql3="UPDATE tabella_risorse SET num_ordini=num_ordini+1 WHERE data='%s' AND reparto_id=%s"%(data_str,this.reparto_id.id)
                            #self.env.cr.execute(sql3)
                            ris.num_ordini = ris.num_ordini + 1                        
                            inizio_ordine=True
                        #sql="UPDATE tabella_risorse SET ore_tot_available=0 WHERE id=%s" %ris.id
                        #self.env.cr.execute(sql)
                        #self.env.cr.commit()
                        ris.ore_tot_available = 0
                        continue

                 
                mrp.write(mrp_data)         
            
            # riporta la situazione a ore_tot_available = ore_tot
            cmd="UPDATE tabella_risorse SET ore_tot_available=ore_tot, num_ordini=0 WHERE reparto_id=%s AND data>='%s'" %(this.reparto_id.id, this.inizializzazione)
            self.env.cr.execute(cmd)
        
               
        return
          
    

class conferma_pianifica_mo(models.TransientModel):

    _name="conferma.pianifica.mo"
    _description="Confirm Manufacturing Order planning"
    
    reparto_id = fields.Many2one('reparti', 'Department', required=True)

    def confirm_plan_mo(self):
        
        for this in self:
        
            oggi=fields.date.today()
            mrp_pool=self.env['mrp.production']
            risorse_pool=self.env['tabella.risorse']
            inizio=datetime(oggi.year,oggi.month,oggi.day,8,0,0) 
            inizio_str=datetime.strftime(inizio,'%Y-%m-%d %H:%M:%S')
#            mrp_ids=mrp_pool.search([('state','not in',('done','progress')),('reparto_id','=',this.reparto_id.id),('planned_start','>=',inizio_str)])
            # uso lo stesso filtro che ho usato per calcolare il calendario
            mrp_ids=mrp_pool.search([('state','not in',('done','progress','cancel')),('reparto_id','=',this.reparto_id.id)])
        
            for mrp in mrp_ids:
                if mrp.planned_start:
                    mrp.date_planned_start = mrp.planned_start  # deve aggiornare anche la settimana
                    #sql="UPDATE mrp_production SET date_planned_start='%s' WHERE id=%s" %(mrp.planned_start,mrp.id)
                    #self.env.cr.execute(sql)                        
       
        return
        
 
