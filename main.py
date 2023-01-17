from tkinter import *
import calendar
import datetime


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
    info_label['text'] = calendar.month_name[month] + ', ' + str(year)
    month_days = calendar.monthrange(year, month)[1]
    if month == 1:
        back_month_days = calendar.monthrange(year - 1, 12)[1]
    else:
        back_month_days = calendar.monthrange(year, month)[1]
    week_day = calendar.monthrange(year, month)[0]

    for n in range(month_days):
        days[n + week_day]['text'] = n + 1
        days[n + week_day]['fg'] = 'black'
        if year == now.year and month == now.month and n == now.day:
            days[week_day]['bg'] = 'green'
            days[n + week_day]['bg'] = 'grey'
        else:
            days[n + week_day]['bg'] = 'grey'

    for n in range(week_day):
        days[week_day - n - 1]['text'] = back_month_days - n
        days[week_day - n - 1]['fg'] = 'gray'
        days[week_day - n - 1]['bg'] = '#f3f3f3'
    for n in range(6 * 7 - month_days - week_day):
        days[week_day + month_days + n]['text'] = n + 1
        days[week_day + month_days + n]['fg'] = 'gray'
        days[week_day + month_days + n]['bg'] = '#f3f3f3'

    print(days)





root = Tk()
root.title('Calendar')
days = []
now = datetime.datetime.now()
year = now.year
month = now.month
back_button = Button(root, text='<', command=back)
back_button.grid(row=0, column=0, sticky=NSEW)
next_button = Button(root, text='>', command=next)
next_button.grid(row=0, column=6, sticky=NSEW)
info_label = Label(root, text=0, width=1, height=1, font='Arial 16 bold', fg='blue')
info_label.grid(row=0, column=1, columnspan=5, sticky=NSEW)

for n in range(7):
    lbl = Label(root, text=calendar.day_abbr[n], width=1, height=1, font='Arial 12 bold', fg='darkblue')
    lbl.grid(row=1, column=n, sticky=NSEW)

for row in range(6):
    for col in range(7):
        lbl = Label(root, text='0', width=4, height=2, font='Arial 14 bold')
        lbl.grid(row=row+2, column=col, sticky=NSEW)
        days.append(lbl)


fill()
root.mainloop()