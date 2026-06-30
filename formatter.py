from tabulate import tabulate
from config import MAX_WIDTH_FTER


def print_main_menu():
    menu = [
        ["1", "Search movies by title"],
        ["2", "Search movies by genre and year"],
        ["3", "Search movies by rating and year"],
        ["4", "Search statistics"],
        ["0", "Exit"],
    ]
    print(tabulate(menu, headers=["", "Main Menu"], tablefmt="fancy_grid"))


def print_menu_statistics():
    menu = [
        ["1", "Top 5 title search requests"],
        ["2", "Top 5 genre and year search requests"],
        ["3", "Top 5 rating and year search requests"],
        ["4", "Last 5 search requests"],
        ["0", "Exit"],
    ]
    print()
    print(tabulate(menu, headers=["", "Search Statistics"], tablefmt="fancy_grid"))


def print_cnt(films_count, search_description):
    if films_count == 0:
        print(f"\nNo movies found for {search_description}")
    else:
        print(
            f"\nFound {films_count} movie(s) for {search_description}\n"
        )


def print_table_films(offset, films, headers):
    headers =[header.capitalize() for header in headers]
    print(f"{f'Movies {offset + 1} - {offset + len(films)}:':^{MAX_WIDTH_FTER}}\n")
    print(tabulate(films, headers=headers, tablefmt="fancy_grid"))


def print_top_searches(data, search_type):
    """
    Formats and prints top search statistics as a table.

    Prepares table headers and rows depending on search type,
    formats year ranges, and displays the result using tabulate.
    """
    
    if not data:
        print("\nNo statistics available yet")
        return

    table = []

    if search_type == "keyword":
        headers = ["Search count", "Keyword", "Found films"]

        for row in data:
            table.append([row["count"], row["keyword"], row["results_count"]])
    elif search_type == "genre & year":
        headers = ["Search count", "Genre", "Year", "Found films"]

        for row in data:
            if row["start_year"] == row["end_year"]:
                year = str(row["start_year"])
            else:
                year = f"{row['start_year']}-{row['end_year']}"

            table.append([row["count"], row["genre"], year, row["results_count"]])
    elif search_type == "rating":
        headers = ["Search count", "Rating", "Year", "Found films"]

        for row in data:
            if row["start_year"] == row["end_year"]:
                year = str(row["start_year"])
            else:
                year = f"{row['start_year']}-{row['end_year']}"

            table.append([row["count"], row["rating"], year, row["results_count"]])

    print()
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def get_query_text(search_type, params):
    if search_type == "keyword":
        return params["keyword"]

    if search_type == "genre & year":
        years = (
            str(params["start_year"])
            if params["start_year"] == params["end_year"]
            else f"{params['start_year']}-{params['end_year']}"
        )
        return f"{params['genre_name']}   |   {years}"

    if search_type == "rating":
        years = (
            str(params["start_year"])
            if params["start_year"] == params["end_year"]
            else f"{params['start_year']}-{params['end_year']}"
        )
        return f"{params['rating']}   |   {years}"

    return str(params)


def print_last_searches(data):
    """
    Formats and prints the last unique search requests.

    Converts search parameters into readable text,
    formats search time, and displays the result as a table.
    """
    
    if not data:
        print("\nNo statistics available yet")
        return

    table = []
    for row in data:
        table.append(
            [
                row["search_type"],
                get_query_text(row["search_type"], row["params"]),
                row["results_count"],
                row["last_search_time"].strftime("%d.%m.%Y %H:%M:%S"),
            ]
        )

    headers = ["Search type", "Query", "Films found", "Last search time"]
    print()
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def print_all_genres(genres):
    print(f"\n{'Movie Genres:':^{MAX_WIDTH_FTER}}")
    headers = ["Id", "Genre"]
    print(tabulate(genres, headers=headers, tablefmt="fancy_grid"))


def print_all_ratings(ratings):
    table = [(i, r[0], r[1]) for i, r in enumerate(ratings, start=1)]
    headers = ["Id", "Rating", "Description"]

    print(f"\n{'Movie Ratings:':^{MAX_WIDTH_FTER}}")
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
