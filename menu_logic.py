import formatter as fter


def convert_input_year(user_year, min_year, max_year):
    """
    Converts user input into start and end year.

    Supports:
    - single year (2005)
    - year range (2000-2005)

    Raises:
        ValueError: If the input format is invalid
        or years are outside the allowed range.
    """
    user_year = user_year.strip()

    if "-" in user_year:
        start, end = user_year.split("-")
        start = int(start.strip())
        end = int(end.strip())

        if start > end or start < min_year or end > max_year:
            raise ValueError
    else:
        start = int(user_year)
        if not min_year <= start <= max_year:
            raise ValueError
        end = start

    return start, end


def call_pagination(pages, films_count):
    """
    Displays film search results page by page.

    Prints one page of results, checks whether all films have been shown,
    and asks the user whether to display the next page.
    """
    for page in pages:
        fter.print_table_films(page["count"], page["films"], page["headers"])
        # все что ниже завернуть в отдлел фцию с параметором page и films_count
        if page["count"] + len(page["films"]) >= films_count:
            print("Это были все найденные фильмы по Вашему запросу")
            break

        while True:
            answer = input("\nПоказать следующие 10 фильмов? y/n : ")

            if answer.strip().lower() == "n":
                show_next = False
                break
            elif answer.strip().lower() == "y":
                show_next = True
                break
            else:
                print(f"\nВведите только y или n")

        if not show_next:
            print()
            break


def search_by_title_menu(db, mongo):
    """
    Handles the menu option for searching films by title keyword.

    The function asks the user to enter a film title or part of a title,
    gets the number of matching films and the film list from MySQL,
    displays results with pagination, and saves successful search
    requests to MongoDB.
    """
    
    while True:
        film_title = input(
            f"\nВведите название/начало названия фильма или 0 для выхода: "
        ).strip()

        if film_title == "0":
            break
        
        if not film_title:
            continue
        
        films_count = db.search_cnt_by_title(film_title)
        fter.print_cnt(films_count, film_title)

        if films_count == 0:
            continue

        mongo.save_log(
            search_type="keyword",
            params={"keyword": film_title},
            results_count=films_count,
        )

        pages = db.search_by_title(film_title, films_count)

        call_pagination(pages, films_count)


def search_by_genre_menu(db, mongo):
    """
    Handles the menu option for searching films by genre and year range.

    The function displays all available genres, validates user input,
    allows searching by a single year or year range, displays results
    with pagination, and saves successful search requests to MongoDB.
    """
    
    all_genres = db.show_all_category()
    genres_dict = dict(all_genres)

    while True:
        fter.print_all_genres(all_genres)

        try:
            genre_id = int(input(f"\nВведите id жанра из списка или 0 для выхода: "))
        except ValueError:
            print("Такого id жанра нет")
            continue

        if genre_id == 0:
            break
        elif genre_id in genres_dict:
            films_count = db.search_cnt_by_genre(genre_id)
            min_year, max_year = db.min_max_years_g(genre_id)

            print(
                f"\nПо жанру {genres_dict[genre_id]} диапазон годов от {min_year} до {max_year}"
            )

            while True:
                user_year = input(
                    "Введите год (хххх), диапазон через тире (хххх-хххх) либо 0 для выбора др жанра: "
                ).strip()

                if user_year == "0":
                    break

                try:
                    start, end = convert_input_year(user_year, min_year, max_year)
                except ValueError:
                    print(
                        f"\nВведите корректный год или диапазон годов (хххх или хххх-хххх)\n"
                    )
                    continue

                films_count = db.search_cnt_by_genre_year(genre_id, start, end)

                search_description = f"жанр {genres_dict[genre_id]} за {user_year} гг."
                fter.print_cnt(films_count, search_description)

                if films_count == 0:
                    continue

                mongo.save_log(
                    search_type="genre & year",
                    params={
                        "genre_name": genres_dict[genre_id],
                        "start_year": start,
                        "end_year": end,
                        "year_filter": "single" if start == end else "range",
                    },
                    results_count=films_count,
                )

                pages = db.search_by_genre_year(genre_id, films_count, start, end)
                call_pagination(pages, films_count)
        else:
            print("Такого id жанра нет")
            continue


def search_by_rating_menu(db, mongo):
    """
    Handles the menu option for searching films by rating and year range.

    The function displays all available film ratings, validates user input,
    allows searching by a single year or year range, displays results
    with pagination, and saves successful search requests to MongoDB.
    """
    
    ratings = db.show_all_ratings()
    ratings_dict = {i: rating[0] for i, rating in enumerate(ratings, start=1)}

    while True:
        fter.print_all_ratings(ratings)

        try:
            rating_id = int(
                input(f"\nВведите id рейтинга из списка или 0 для выхода: ")
            )
        except ValueError:
            print("Такого id рейтинга нет")
            continue

        if rating_id == 0:
            break

        elif rating_id in ratings_dict:
            user_rating = ratings_dict[rating_id]
            films_count = db.search_cnt_by_rating(user_rating)
            min_year, max_year = db.min_max_years_r(user_rating)
            print(
                f"\nПо рейтингу {user_rating} диапазон годов от {min_year} до {max_year}"
            )

            while True:
                user_year = input(
                    "Введите год (хххх), диапазон через тире (хххх-хххх) либо 0 для выбора др рейтинга: "
                ).strip()

                if user_year == "0":
                    break

                try:
                    start, end = convert_input_year(user_year, min_year, max_year)
                except ValueError:
                    print(
                        f"\nВведите корректный год или диапазон годов (хххх или хххх-хххх)\n"
                    )
                    continue

                films_count = db.search_cnt_by_rating_year(user_rating, start, end)
                search_description = f"рейтинг {user_rating} за {user_year} гг."
                fter.print_cnt(films_count, search_description)

                if films_count == 0:
                    continue

                mongo.save_log(
                    search_type="rating",
                    params={
                        "rating": user_rating,
                        "start_year": start,
                        "end_year": end,
                        "year_filter": "single" if start == end else "range",
                    },
                    results_count=films_count,
                )

                pages = db.search_by_rating_year(user_rating, films_count, start, end)
                call_pagination(pages, films_count)
        else:
            print("Такого id рейтинга нет")
            continue


def statistics_menu(db, mongo):
    """
    Handles the statistics menu.

    Allows the user to view:
    - top search requests by title
    - top search requests by genre and year
    - top search requests by rating and year
    - last unique search requests
    """
    
    while True:
        fter.print_menu_statistics()

        try:
            stat_choice = int(input("\nВыберите пункт меню статистики: "))
        except ValueError:
            print(f"\nВведите число из меню (1, 2, 3, 4 или 0)")
            continue

        if stat_choice == 1:
            search_type = "keyword"
            data = mongo.get_top_searches(search_type)
            fter.print_top_searches(data, search_type)
        elif stat_choice == 2:
            search_type = "genre & year"
            data = mongo.get_top_searches(search_type)
            fter.print_top_searches(data, search_type)
        elif stat_choice == 3:
            search_type = "rating"
            data = mongo.get_top_searches(search_type)
            fter.print_top_searches(data, search_type)
        elif stat_choice == 4:
            data = mongo.get_last_searches()
            fter.print_last_searches(data)
        elif stat_choice == 0:
            break
        else:
            print(f"\nВведите корректный пункт меню (1, 2, 3, 4 или 0)")
