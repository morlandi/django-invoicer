import xlrd

##########################################################################################
# XlsPriceImporter

class XlsImporter(object):

    def __init__(self, request, attachment, klass ):
        self.requeste = request
        self.attachment = attachment
        self.klass = klass

    def _setup(self):
        self.workbook = xlrd.open_workbook(file_contents=self.attachment.read())
        self.worksheet = self.workbook.sheet_by_index(0)

    def _tear_down(self):
        pass

    def _import_single_price(self, nrow):

        # retrieve tag
        tag_cell = self.worksheet.cell(nrow,0)
        if tag_cell.ctype == 2:
            tag = str(int(tag_cell.value))
        else:
            tag = tag_cell.value

        # retrieve cost
        cost = float(self.worksheet.cell(nrow,1).value)

        queryset = self.price_klass.objects.filter(system=self.system, tag=tag)
        n = queryset.count()
        if n <= 0:
            if tag not in self.bad_tags:
                self.bad_tags.append(tag)
        else:
            queryset.update(cost=cost, modified_by=self.user, date_modified=datetime.today())

        return n

    def import_all_rows(self):

        count = 0
        self._setup()

        # scan worksheet
        line = 1
        for nrow in range(1,self.worksheet.nrows):
            line = line+1
            try:
                #n = self._import_single_price(nrow)
                pass
            except Exception, e:
                error_message = (_(u"ERROR at line %d: ") % line) + e.message
                raise Exception(error_message)

        self._tear_down()

        return line-1

