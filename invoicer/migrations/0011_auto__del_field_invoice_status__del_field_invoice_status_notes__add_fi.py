# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Invoice.status'
        db.delete_column('invoicer_invoice', 'status')

        # Deleting field 'Invoice.status_notes'
        db.delete_column('invoicer_invoice', 'status_notes')

        # Adding field 'Invoice.locked'
        db.add_column('invoicer_invoice', 'locked', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Invoice.paid'
        db.add_column('invoicer_invoice', 'paid', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Invoice.notes'
        db.add_column('invoicer_invoice', 'notes', self.gf('django.db.models.fields.TextField')(default='', max_length=512, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Invoice.status'
        db.add_column('invoicer_invoice', 'status', self.gf('django.db.models.fields.CharField')(default='unsent', max_length=10), keep_default=False)

        # Adding field 'Invoice.status_notes'
        db.add_column('invoicer_invoice', 'status_notes', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True), keep_default=False)

        # Deleting field 'Invoice.locked'
        db.delete_column('invoicer_invoice', 'locked')

        # Deleting field 'Invoice.paid'
        db.delete_column('invoicer_invoice', 'paid')

        # Deleting field 'Invoice.notes'
        db.delete_column('invoicer_invoice', 'notes')


    models = {
        'invoicer.client': {
            'Meta': {'object_name': 'Client'},
            'administrative_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'delivery_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fiscal_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'invoicer.company': {
            'Meta': {'object_name': 'Company'},
            'billing_email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'use_compact_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'invoicer.invoice': {
            'Meta': {'ordering': "('-year', '-number')", 'unique_together': "(('company', 'number', 'year'),)", 'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Client']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Company']"}),
            'due_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'null': 'True', 'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'left_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2'}),
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
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1'", 'max_digits': '7', 'decimal_places': '2'}),
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
