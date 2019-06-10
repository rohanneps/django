from django.contrib.admin.filters import FieldListFilter

class DropdownFilter(FieldListFilter):
    template = 'admin/dropdown_filter.html'