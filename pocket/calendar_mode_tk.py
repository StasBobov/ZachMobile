from pprint import pprint
import tkinter as tk
import calendar
import datetime
from functools import partial


def back():
    global month, year
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    fill()


def next():
    global month, year
    month += 1
    if month == 13:
        month = 1
        year += 1
    fill()



def fill():
    # инфо табло/calendar.month_name[month] - текущий месяц  + текущий год
    info_label['text'] = calendar.month_name[month] + ', ' + str(year)
    # calendar.monthrange(year, month)[1] - дней в текущем месяце текущего года
    month_days = calendar.monthrange(year, month)[1]
    # если январь
    if month == 1:
        # дней в декабре прошлого года
        back_month_days = calendar.monthrange(year - 1, 12)[1]
    else:
        # дней в прошлом месяце прошлого года
        back_month_days = calendar.monthrange(year, month - 1)[1]
    # первый день месяца (понедельник - 0)
    week_day = calendar.monthrange(year, month)[0]

    # n - дни текущего месяца текущего года с 0
    for n in range(month_days):
        # в списке объекту Button по индексам дням присваиваются числа в поле text
        days[n + week_day]['text'] = n + 1
        days[n + week_day]['fg'] = 'black'
        if year == now.year and month == now.month and n == now.day:
            # красим сегодняшний день в зеленый
            days[now.day + week_day -1]['bg'] = 'green'
            # остальные дни - серым
            days[n + week_day]['bg'] = 'grey'
        else:
            days[n + week_day]['bg'] = 'grey'

    # заполняем дни предыдущего месяца
    for n in range(week_day):
        days[week_day - n - 1]['text'] = back_month_days - n
        days[week_day - n - 1]['fg'] = 'gray'
        days[week_day - n - 1]['bg'] = '#f3f3f3'
    # заполняем дни следующего месяца
    for n in range(6 * 7 - month_days - week_day):
        days[week_day + month_days + n]['text'] = n + 1
        days[week_day + month_days + n]['fg'] = 'gray'
        days[week_day + month_days + n]['bg'] = '#f3f3f3'


def button_info(event):
    # вычисляем дату, написанную на кнопке
    day = event.widget['text']
    print(day, month, year)





root = tk.Tk()
root.title('Calendar')
days = []
now = datetime.datetime.now()
year = now.year
month = now.month
back_button = tk.Button(root, text='<', command=back)
back_button.grid(row=0, column=0, sticky=tk.NSEW)
next_button = tk.Button(root, text='>', command=next)
next_button.grid(row=0, column=6, sticky=tk.NSEW)
info_label = tk.Label(root, text=0, width=1, height=1, font='Arial 16 bold', fg='blue')
info_label.grid(row=0, column=1, columnspan=5, sticky=tk.NSEW)

for n in range(7):
    day_of_week = tk.Label(root, text=calendar.day_abbr[n], width=1, height=1, font='Arial 12 bold', fg='darkblue')
    day_of_week.grid(row=1, column=n, sticky=tk.NSEW)

for row in range(6):
    for col in range(7):
        _date = tk.Button(root, text='0', width=2, height=1, font='Arial 14 bold')
        _date.bind('<Button-1>', partial(button_info))
        _date.grid(row=row+2, column=col, sticky=tk.NSEW)
        # заполнили словарь объектами с текстом 0
        days.append(_date)


# pprint(dir(days[0]))
fill()
root.mainloop()