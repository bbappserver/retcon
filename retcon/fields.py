from django.db import models
import re
import d

class PartialDate():

    PRECISION_DAY=0x0
    PRECISION_MONTH=0x1
    PRECISION_YEAR=0x2
    regex = re.compile(r"((?:\d|\*|x|y){1,4})-((?:\d|\*|x|m){1,2})-((?:\d|\*|x|d){1,2})")

    def __init__(self,val):
        self._date=None
        self._precision=self.PRECISION_DAY
        if isinstance(str,val):
            #parse
            items=self.regex.findall(val)
            #check that precision is monotonic
        elif isinstance(int,val):
            #setinternal
            self._date=self.from_db_repr(value)
        elif isinstance (date,val):
            self._date=val
        else:
            raise ValueError()
    
    def from_db_repr(self,value):
        days= value >> 2
        self._precision= value & 0x2
        self._date= date.fromordinal(days)

    def db_repr(self):
        days=date.toordinal()
        if (0xC0000000 & days) !=0:
            raise OverflowError("The provided date istoo big to fit in packed format")
        pack=days<<2
        pack&=self._precision
        return pack
    
    def string_repr(self):
        if self._precision== self.PRECISION_DAY:
            fmt="YYYY-MM-DD"
            raise
        elif self._precision== self.PRECISION_MONTH:
            fmt="YYYY-MM-**"
            raise
        elif self._precision== self.PRECISION_YEAR:
            fmt="YYYY-**-**"


    


class PartialDateField(models.Field):
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return PartialDate(int(value))

    def to_python(self, value):
        if isinstance(value, PartialDate):
            return value

        if value is None:
            return value

        return PartialDate(value)

    def get_internal_type(self):
        return 'IntegerField'
    
    def get_prep_value(self, value):
        return value.db_repr()
    
    def value_to_string(self,obj):
        value = self.value_from_object(obj)
        return value.string_repr()

class TinyIntegerField(models.SmallIntegerField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return "tinyint"
        else:
            return super(TinyIntegerField, self).db_type(connection)

class PositiveTinyIntegerField(models.PositiveSmallIntegerField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return "tinyint unsigned"
        else:
            return super(PositiveTinyIntegerField, self).db_type(connection)