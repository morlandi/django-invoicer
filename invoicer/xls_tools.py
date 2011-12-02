import xlrd
from django.utils.translation import ugettext_lazy as _
from invoicer.models import Client
from invoicer.models import Invoice
from time import strptime
from decimal import Decimal
from invoicer.utils import get_company
from datetime import date

##########################################################################################
# XlsPriceImporter

class XlsImporter(object):

    def __init__(self, request, attachment, klass ):
        self.requeste = request
        self.attachment = attachment
        self.klass = klass
        self.columns = {}

    def _setup(self):
        self.workbook = xlrd.open_workbook(file_contents=self.attachment.read())
        sheet_name = ''
        if self.klass==Client:
            sheet_name = 'Clienti'
        elif self.klass==Invoice:
            sheet_name = 'Fatture'
        else:
            raise Exception(u'Unknown class: ' + str(self.klass))
        self.worksheet = self.workbook.sheet_by_name(sheet_name)

    def _tear_down(self):
        pass

    def _scan_worksheet_columns(self):
        for ncol in range(0,self.worksheet.ncols):
            cell = self.worksheet.cell(0,ncol)
            key = str(cell.value).strip().lower()
            self.columns[key] = ncol

    def _read_cell(self, nrow, column_name):
        ncol = self.columns[column_name.lower()]
        cell = self.worksheet.cell(nrow,ncol)
        return str(cell.value).strip()

    def _read_cell_as_int(self, nrow, column_name):
        text = self._read_cell(nrow, column_name)
        return int(float(text))

    def _read_cell_as_date(self, nrow, column_name):
        text = self._read_cell(nrow, column_name)
        if len(text)>0:
            st = strptime(text, "%d/%m/%Y")
            return date(*st[0:3])
        return None

    def _import_single_client(self, nrow):

        def mk_address(columns):
            tokens = []
            for column in columns:
                text = self._read_cell(nrow, column)
                if len(text): 
                    tokens.append(text)
            return '\n'.join(tokens)
   
        name = self._read_cell(nrow,'ragione sociale')
        vat_id = self._read_cell(nrow,'p.iva.')
        if ' ' in vat_id:
            # remove leading description if any
            tokens = vat_id.split(' ')
            vat_id = tokens[-1]
        fiscal_code = self._read_cell(nrow, 'codice fiscale')
        email = self._read_cell(nrow, 'email')
        bank_address = self._read_cell(nrow, 'banca d\'appoggio')

        address1 = mk_address(['via (spedizione)', 'citta\'', ])
        address2 = mk_address(['indirizzo per fatturazione (via)', 'indirizzo per fatturazione (citta)', ])
        if len(address2)<=0:
            administrative_address = address1
            delivery_address = ''
        else:   
            administrative_address = address2
            delivery_address = address1

        client = Client( name=name, vat_id=vat_id, fiscal_code=fiscal_code, email=email, administrative_address=administrative_address, delivery_address=delivery_address)
        client.save()

    def _import_single_invoice(self, nrow):

        def client_lookup(client_name):
            return Client.objects.get(name=client_name)

    
    # paid_date = models.DateField(null=True, blank=True)
    # notes = models.TextField(max_length=512, blank=True)
    # net_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    # gross_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

        number = self._read_cell_as_int(nrow, 'n.')
        year = self._read_cell_as_int(nrow, 'year')
        company = get_company()
        invoice_date = self._read_cell_as_date(nrow, 'data')
        client = client_lookup(self._read_cell(nrow, 'cliente'))
        location = company.location
        tax_rate = Decimal(self._read_cell(nrow, 'taxrate'))
        if len(client.delivery_address)==0:
            left_address = ''
            right_address = client.administrative_address
        else:
            right_address = client.delivery_address
            left_address = client.administrative_address
        due_date = self._read_cell_as_date(nrow, 'scadenza')
        terms = self._read_cell(nrow, 'pag.')

        footer = company.invoice_footer
        locked = False
        paid = True
        #paid_date = self._read_cell_as_date(nrow, 'pagato')

        # print '-'*50
        # print '%d / %d' % (number, year)
        # print '-'*50
        # print company
        # print invoice_date
        # print client
        # print location
        # print tax_rate
        # print left_address
        # print right_address
        # print due_date
        # print terms
        # print footer
        # print locked
        # print paid
        # #print paid_date

        invoice = Invoice(number=number, year=year, company=company, invoice_date=invoice_date, client=client, location=location,
            tax_rate=tax_rate, left_address=left_address, right_address=right_address, due_date=due_date, terms=terms,
            footer=footer, locked=locked, paid=paid)
        invoice.save()

    def import_all_rows(self):

        self._setup()

        # scan worksheet
        self._scan_worksheet_columns()
        for nrow in range(1,self.worksheet.nrows):

            try:
                if self.klass==Client:
                    self._import_single_client(nrow)
                elif self.klass==Invoice:
                    self._import_single_invoice(nrow)
                else:
                    raise Exception(u'Unknown class: ' + str(self.klass))
            except Exception, e:
                error_message = (_(u"ERROR at line %d: ") % (nrow+1)) + e.message
                raise Exception(error_message)

        self._tear_down()

        return nrow

