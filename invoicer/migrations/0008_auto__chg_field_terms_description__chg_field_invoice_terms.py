# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Terms.description'
        db.alter_column('invoicer_terms', 'description', self.gf('django.db.models.fields.TextField')(max_length=512))

        # Renaming column for 'Invoice.terms' to match new field type.
        db.rename_column('invoicer_invoice', 'terms_id', 'terms')
        # Changing field 'Invoice.terms'
        db.alter_column('invoicer_invoice', 'terms', self.gf('django.db.models.fields.TextField')(default='', max_length=512))

        # Removing index on 'Invoice', fields ['terms']
        db.delete_index('invoicer_invoice', ['terms_id'])


    def backwards(self, orm):
        
        # Adding index on 'Invoice', fields ['terms']
        db.create_index('invoicer_invoice', ['terms_id'])

        # Changing field 'Terms.description'
        db.alter_column('invoicer_terms', 'description', self.gf('django.db.models.fields.TextField')(max_length=256))

        # Renaming column for 'Invoice.terms' to match new field type.
        db.rename_column('invoicer_invoice', 'terms', 'terms_id')
        # Changing field 'Invoice.terms'
        db.alter_column('invoicer_invoice', 'terms_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Terms'], null=True))


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
            'due_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'left_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'right_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unsent'", 'max_length': '10'}),
            'status_notes': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
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
            'Meta': {'object_name': 'LineItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line_items'", 'to': "orm['invoicer.Invoice']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Item']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
