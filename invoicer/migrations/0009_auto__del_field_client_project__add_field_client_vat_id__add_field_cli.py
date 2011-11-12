# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Client.project'
        db.delete_column('invoicer_client', 'project')

        # Adding field 'Client.vat_id'
        db.add_column('invoicer_client', 'vat_id', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True), keep_default=False)

        # Adding field 'Client.administrative_address'
        db.add_column('invoicer_client', 'administrative_address', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Client.delivery_address'
        db.add_column('invoicer_client', 'delivery_address', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Client.project'
        db.add_column('invoicer_client', 'project', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True), keep_default=False)

        # Deleting field 'Client.vat_id'
        db.delete_column('invoicer_client', 'vat_id')

        # Deleting field 'Client.administrative_address'
        db.delete_column('invoicer_client', 'administrative_address')

        # Deleting field 'Client.delivery_address'
        db.delete_column('invoicer_client', 'delivery_address')


    models = {
        'invoicer.client': {
            'Meta': {'object_name': 'Client'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'administrative_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'delivery_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'invoicer.company': {
            'Meta': {'object_name': 'Company'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'billing_email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invoice_stylesheet': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numbering_prefix': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'use_compact_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '100', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'invoicer.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Client']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Company']"}),
            'due_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status_notes': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'terms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Terms']"})
        },
        'invoicer.item': {
            'Meta': {'object_name': 'Item'},
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'invoicer.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line_items'", 'to': "orm['invoicer.Invoice']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Item']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1'", 'max_digits': '7', 'decimal_places': '2'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'invoicer.stylesheet': {
            'Meta': {'object_name': 'Stylesheet'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stylesheets'", 'to': "orm['invoicer.Company']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'feedback_text': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction_text': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'misc_text': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'stylesheet': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'thank_you_text': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'})
        },
        'invoicer.terms': {
            'Meta': {'object_name': 'Terms'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['invoicer']
