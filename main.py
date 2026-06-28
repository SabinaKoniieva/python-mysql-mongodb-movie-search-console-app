import pymysql
import pymongo
import formatter as fter
from config import dbconfig, mongoconfig
from MySQL import DB
from MongoDB import MongoDB
from menu_logic import search_by_title_menu, search_by_genre_menu, search_by_rating_menu, statistics_menu


def main():
    try:
        db = DB(dbconfig)
    except pymysql.err.OperationalError:
        print("Ошибка подключения к MySQL")
        return

    try:
        mongo = MongoDB(mongoconfig)
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Ошибка подключения к MongoDB")
        return
        
    while True:
        fter.print_main_menu()

        try:
            user_choice = int(input(f"\nВыберите пункт меню: "))
        except ValueError:
            print(f"\nВведите именно цифру меню (1, 2, 3, 4 или 0)")
            continue

        if user_choice == 1:
            search_by_title_menu(db, mongo)
        elif user_choice == 2:
            search_by_genre_menu(db, mongo)
        elif user_choice == 3:
            search_by_rating_menu(db, mongo)
        elif user_choice == 4:
            statistics_menu(db, mongo)
        elif user_choice == 0:
            print(f"\nРабота приложения завершена!")
            print(f"Спасибо за использование!")
            break
        else:
            print(f"\nВведите корректное число (1, 2, 3, 4 или 0)")
    
    db.close()
    mongo.close()


main()
