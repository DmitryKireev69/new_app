import os
from time import sleep
from pythonping import ping
import PySimpleGUI as sg
import sqlite3

users_ips = []
users = []

def load():
    global database
    database = r'\\192.168.33.253\software\database\users.db'
    global db
    db = sqlite3.connect(database)
    global sql
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS logins (
        login TEXT
    )""")

    sql.execute("""CREATE TABLE IF NOT EXISTS ips (
          ip TEXT
      )""")

    db.commit()

    for value in sql.execute("SELECT * FROM logins"):
        users.append(value[0])


    for value in sql.execute("SELECT * FROM ips"):
        users_ips.append(value[0])


def addUser(login, window):
    if sql.execute('''SELECT login FROM logins WHERE login = ?''', (login,)).fetchone() is None:
        sql.execute("INSERT INTO logins VALUES (?)", (login,))
        db.commit()
        users.append(login)
        window['listBoxLogin'].update(users)
        window['login'].update([])
    else:
        window['login'].update([])
        sg.popup_error_with_traceback('Такая запись уже имееться')


def addAddress(address, window):
    if sql.execute('''SELECT ip FROM ips WHERE ip = ?''',
                   (address,)).fetchone() is None:
        sql.execute("INSERT INTO ips VALUES (?)", (address,))
        db.commit()
        users_ips.append(address)
        window['listBoxAddress'].update(users_ips)
        window['address'].update([])
    else:
        window['address'].update([])
        sg.popup_error_with_traceback('Такая запись уже имееться')

def deleteAddress(address):
    sql.execute('''DELETE FROM ips WHERE ip = ?''', (address,))
    db.commit()

def deleteLogin(login):
    sql.execute('''DELETE FROM logins WHERE login = ?''', (login,))
    db.commit()

def interface():
    layout = [
        [
            sg.Submit('Добавить login', key='btnAddLogin', size=(13, 1)),
            sg.InputText(size=20, key='login'),
            sg.Submit('Добавить ip', key='btnAddIp', size=(13, 1)),
            sg.InputText(size=20, key='address')
         ],
        [
            sg.Submit('Удалить login', key='btnDeleteLogin', size=(13, 1)),
            sg.InputText(size=20, key='deleteLogin'),
            sg.Submit('Удалить ip', key='btnDeleteIp', size=(13, 1)),
            sg.InputText(size=20, key='deleteAddress')
        ],
        [sg.Text('Пользователи', size=(30, 1)), sg.Text('Адреса компьютеров')],
        [
            sg.Listbox(values=users, size=(35, 10), key='listBoxLogin'),
            sg.Listbox(values=users_ips, size=(35, 10), key='listBoxAddress')
        ],
        [sg.Submit('Удалить OST', key='btnDeleteOst')]
    ]
    window = sg.Window('Delete OST', layout)
    while True:
        event, values = window.read()
        if event == 'btnAddLogin':
            addUser(values['login'], window)
        elif event == 'btnDeleteLogin':
            deleteLogin(values['deleteLogin'])
            if values['deleteLogin'] in users:
                users.remove(values['deleteLogin'])
                window['deleteLogin'].update([])
            else:
                window['deleteLogin'].update([])

            window['listBoxLogin'].update(users)
        elif event == 'btnAddIp':
            addAddress(values['address'], window)
        elif event == 'btnDeleteIp':
            deleteAddress(values['deleteAddress'])
            if values['deleteAddress'] in users_ips:
                users_ips.remove(values['deleteAddress'])
                window['deleteAddress'].update([])
            else:
                window['deleteAddress'].update([])
            window['listBoxAddress'].update(users_ips)
        elif event == 'btnDeleteOst':
            deleteOST()
        if event in (None, 'Exit', 'Cancel'):
            break


def deleteOST():
    for i, ip in enumerate(users_ips):
        sg.one_line_progress_meter('Выполнение программы', i + 1, len(users_ips),
                                   'Очистка ost файлов: Ожидайте!')
        if ping(ip).success():
            for user in users:
                os.system(
                    f"taskkill /s {ip} /u tvk\suppadm /p ******** /im outlook.exe /f")
                sleep(1)
                try:
                    os.remove(
                        f'//{ip}/c$/Users/{user}/AppData/Local/Microsoft/Outlook/{user}@tvervodokanal.ru.ost')
                except Exception as e:
                    print('Process failed', e)

def main():
    load(),
    interface()


if __name__ == '__main__':
    main()