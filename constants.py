from datetime import timedelta

BEFORE_WEEK = timedelta(days=7)
BEFORE_DAY = timedelta(days=1)
MONTHES = {'январь': 31, 'февраль': 29, 'март': 31, 'апрель': 30,
           'май': 31, 'июнь': 30, 'июль': 31, 'август': 31,
           'сентярь': 30, 'октябрь': 31, 'ноябрь': 30, 'декабрь': 31}
MONTHES_ENUM = {'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
                'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
                'сентярь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12}
TOKEN = '6801000433:AAFxb9rCFs8dtZukC_Peu9ZgIYlGuew4gG0'