# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Client'
        db.create_table('invoicer_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('vat_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('fiscal_code', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=80, blank=True)),
            ('administrative_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('delivery_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bank_address', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('invoicer', ['Client'])

        # Adding model 'Company'
        db.create_table('invoicer_company', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=80, blank=True)),
            ('invoice_tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('use_compact_invoice', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=512, blank=True)),
            ('invoice_footer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bank_address', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('invoicer', ['Company'])

        # Adding model 'Terms'
        db.create_table('invoicer_terms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=512)),
        ))
        db.send_create_signal('invoicer', ['Terms'])

        # Adding model 'LineItem'
        db.create_table('invoicer_lineitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='line_items', to=orm['invoicer.Invoice'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Item'], null=True, blank=True)),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default='1', max_digits=8, decimal_places=2)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal('invoicer', ['LineItem'])

        # Adding model 'Invoice'
        db.create_table('invoicer_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['invoicer.Company'])),
            ('invoice_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['invoicer.Client'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('left_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('right_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('terms', self.gf('django.db.models.fields.TextField')(max_length=512, blank=True)),
            ('footer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=512, blank=True)),
            ('net_total', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
            ('gross_total', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('invoicer', ['Invoice'])

        # Adding unique constraint on 'Invoice', fields ['company', 'number', 'year']
        db.create_unique('invoicer_invoice', ['company_id', 'number', 'year'])

        # Adding model 'Item'
        db.create_table('invoicer_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('invoicer', ['Item'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Invoice', fields ['company', 'number', 'year']
        db.delete_unique('invoicer_invoice', ['company_id', 'number', 'year'])

        # Deleting model 'Client'
        db.delete_table('invoicer_client')

        # Deleting model 'Company'
        db.delete_table('invoicer_company')

        # Deleting model 'Terms'
        db.delete_table('invoicer_terms')

        # Deleting model 'LineItem'
        db.delete_table('invoicer_lineitem')

        # Deleting model 'Invoice'
        db.delete_table('invoicer_invoice')

        # Deleting model 'Item'
        db.delete_table('invoicer_item')


    models = {
        'invoicer.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'administrative_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'delivery_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'fiscal_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'invoicer.company': {
            'Meta': {'object_name': 'Company'},
            'bank_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invoice_tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'use_compact_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'invoicer.invoice': {
            'Meta': {'ordering': "('-year', '-number')", 'unique_together': "(('company', 'number', 'year'),)", 'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Client']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Company']"}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gross_total': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'left_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'net_total': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'right_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'terms': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'invoicer.item': {
            'Meta': {'object_name': 'Item'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'invoicer.lineitem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'LineItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line_items'", 'to': "orm['invoicer.Invoice']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Item']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1'", 'max_digits': '8', 'decimal_places': '2'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'invoicer.terms': {
            'Meta': {'object_name': 'Terms'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['invoicer']
