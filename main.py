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
        print("Failed to connect to MySQL.")
        return

    try:
        mongo = MongoDB(mongoconfig)
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB.")
        return
        
    while True:
        fter.print_main_menu()

        try:
            user_choice = int(input(f"\nSelect a menu option: "))
        except ValueError:
            print(f"\nPlease enter a number (1, 2, 3, 4, or 0)")
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
            print(f"\nApplication closed.")
            print(f"Thank you for using the application!")
            break
        else:
            print(f"\nPlease enter a valid menu option (1, 2, 3, 4, or 0)")
    
    db.close()
    mongo.close()


main()
