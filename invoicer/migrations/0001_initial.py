# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Company'
        db.create_table('invoicer_company', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=80, blank=True)),
            ('invoice_tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('use_compact_invoice', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=512, blank=True)),
            ('invoice_footer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bank_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('custom_styles', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('invoicer', ['Company'])

        # Adding M2M table for field authorized_users on 'Company'
        db.create_table('invoicer_company_authorized_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('company', models.ForeignKey(orm['invoicer.company'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('invoicer_company_authorized_users', ['company_id', 'user_id'])

        # Adding model 'Client'
        db.create_table('invoicer_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Company'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('vat_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('fiscal_code', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=80, blank=True)),
            ('administrative_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('delivery_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bank_address', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('invoicer', ['Client'])

        # Adding model 'Terms'
        db.create_table('invoicer_terms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Company'])),
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
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Company'])),
            ('serial', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
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
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoicer.Company'])),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('invoicer', ['Item'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Invoice', fields ['company', 'number', 'year']
        db.delete_unique('invoicer_invoice', ['company_id', 'number', 'year'])

        # Deleting model 'Company'
        db.delete_table('invoicer_company')

        # Removing M2M table for field authorized_users on 'Company'
        db.delete_table('invoicer_company_authorized_users')

        # Deleting model 'Client'
        db.delete_table('invoicer_client')

        # Deleting model 'Terms'
        db.delete_table('invoicer_terms')

        # Deleting model 'LineItem'
        db.delete_table('invoicer_lineitem')

        # Deleting model 'Invoice'
        db.delete_table('invoicer_invoice')

        # Deleting model 'Item'
        db.delete_table('invoicer_item')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'invoicer.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'administrative_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Company']"}),
            'delivery_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'fiscal_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'invoicer.company': {
            'Meta': {'object_name': 'Company'},
            'authorized_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'bank_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'custom_styles': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invoice_tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'use_compact_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'invoicer.invoice': {
            'Meta': {'ordering': "('-serial',)", 'unique_together': "(('company', 'number', 'year'),)", 'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['invoicer.Client']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Company']"}),
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
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'terms': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'invoicer.item': {
            'Meta': {'object_name': 'Item'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Company']"}),
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
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoicer.Company']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['invoicer']
