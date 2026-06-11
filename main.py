import pymysql
import pymongo
import formatter as fter
from config import dbconfig, mongoconfig
from MySQL import DB
from MongoDB import MongoDB
from menu_logic import menu_1, menu_2, menu_3, menu_4


def main():
    while True:
        fter.print_main_menu()

        try:
            user_choice = int(input(f"\nВыберите пункт меню: "))
        except ValueError:
            print(f"\nВведите именно цифру меню (1, 2, 3, 4 или 0)")
            continue

        try:
            db = DB(dbconfig)
        except pymysql.err.OperationalError:
            print("Ошибка подключения к MySQL")
            continue

        try:
            mongo = MongoDB(mongoconfig)
        except pymongo.errors.ServerSelectionTimeoutError:
            print("Ошибка подключения к MongoDB")
            continue

        if user_choice == 1:
            menu_1(db, mongo)
        elif user_choice == 2:
            menu_2(db, mongo)
        elif user_choice == 3:
            menu_3(db, mongo)
        elif user_choice == 4:
            menu_4(db, mongo)
        elif user_choice == 0:
            print(f"\nРабота приложения завершена!")
            print(f"Спасибо за использование!")
            break
        else:
            print(f"\nВведите корректное число (1, 2, 3, 4 или 0)")


main()
