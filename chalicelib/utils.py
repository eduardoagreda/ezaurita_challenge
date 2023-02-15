from datetime import datetime

class DateTimeFormat:

    @classmethod
    def convert_date(self, date):
        return datetime.strftime(date, '%d/%m/%Y, %H:%M:%S')