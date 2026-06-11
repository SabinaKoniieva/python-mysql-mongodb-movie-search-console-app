import pymysql


class DB:
    def __init__(self, config):
        self.connection = pymysql.connect(**config)

    def search_cnt_by_title(self, film_title):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT COUNT(*) as films_count
                FROM film
                WHERE title LIKE %s
            """
            cursor.execute(query_cnt, (f"%{film_title}%",))
            return cursor.fetchone()[0]

    def search_cnt_by_genre(self, genre_id):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT COUNT(*)
                FROM film AS f
                JOIN film_category AS fc ON f.film_id = fc.film_id
                JOIN category AS c ON fc.category_id = c.category_id
                WHERE fc.category_id = %s
            """
            cursor.execute(query_cnt, (genre_id,))
            return cursor.fetchone()[0]

    def search_cnt_by_rating(self, rating):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT COUNT(*)
                FROM film
                WHERE rating = %s
            """
            cursor.execute(query_cnt, (rating,))
            return cursor.fetchone()[0]

    def search_cnt_by_genre_year(self, genre_id, start, end):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT count(*) 
                FROM film AS f
                JOIN film_category AS fc ON f.film_id = fc.film_id
                JOIN category AS c ON c.category_id = fc.category_id
                WHERE c.category_id = %s AND f.release_year BETWEEN %s AND %s
            """
            cursor.execute(query_cnt, (genre_id, start, end))
            return cursor.fetchone()[0]

    def search_cnt_by_rating_year(self, rating, start, end):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT count(*) 
                FROM film
                WHERE rating = %s AND release_year BETWEEN %s AND %s
            """
            cursor.execute(query_cnt, (rating, start, end))
            return cursor.fetchone()[0]

    def min_max_years_g(self, genre_id):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT 
                    MIN(CAST(f.release_year AS UNSIGNED)) as min,
                    MAX(CAST(f.release_year AS UNSIGNED)) as max
                FROM film AS f
                JOIN film_category AS fc ON f.film_id = fc.film_id
                JOIN category AS c ON fc.category_id = c.category_id
                WHERE fc.category_id = %s
            """
            cursor.execute(query_cnt, (genre_id,))
            return cursor.fetchone()

    def min_max_years_r(self, rating):
        with self.connection.cursor() as cursor:
            query_cnt = """
                SELECT 
                    MIN(CAST(release_year AS UNSIGNED)) as min,
                    MAX(CAST(release_year AS UNSIGNED)) as max
                FROM film 
                WHERE rating = %s
            """
            cursor.execute(query_cnt, (rating,))
            return cursor.fetchone()

    def paginate(self, query, params=(), total_count=0, limit=10):
        """
        Returns query results page by page using LIMIT and OFFSET.

        Executes the SQL query with pagination parameters,
        fetches films in portions, and yields dictionaries
        containing film data, headers, and current offset.
        """
        
        offset = 0

        with self.connection.cursor() as cursor:
            while offset < total_count:
                cursor.execute(query, (*params, limit, offset))
                films = cursor.fetchall()

                if not films:
                    break

                yield {
                    "count": offset,
                    "films": films,
                    "headers": [column[0] for column in cursor.description],
                }
                offset += limit

    def show_all_category(self):
        with self.connection.cursor() as cursor:
            query = " SELECT category_id, name FROM category"
            cursor.execute(query)
            return cursor.fetchall()

    def show_all_ratings(self):
        with self.connection.cursor() as cursor:
            query = """
                SELECT DISTINCT rating,
                    CASE
                        WHEN rating = 'G' THEN 'The film is shown without restrictions'
                        WHEN rating = 'R' THEN 'Children <17 years of age must be accompanied by a parent or legal guardian'
                        WHEN rating = 'NC-17' THEN 'This film is not suitable for children 17 years of age or younger'
                        WHEN rating = 'PG-13' THEN 'Viewing is not recommended for children <13'
                        WHEN rating = 'PG' THEN 'Children are advised to watch this film with parents'
                    END AS description
                FROM film
                ORDER BY FIELD(rating, 'G', 'PG', 'PG-13', 'R', 'NC-17')
            """
            cursor.execute(query)
            return cursor.fetchall()

    def search_by_title(self, film_title, films_count):
        if films_count == 0:
            return

        query_list = """
            SELECT f.title, f.release_year as year, c.name AS genre, f.rating
            FROM film AS f
            JOIN film_category AS fc ON f.film_id = fc.film_id
            JOIN category AS c ON fc.category_id = c.category_id
            WHERE f.title LIKE %s
            LIMIT %s OFFSET %s
        """

        return self.paginate(
            query=query_list, params=(f"%{film_title}%",), total_count=films_count
        )

    def search_by_genre_year(self, genre_id, films_count, start, end):
        if films_count == 0:
            return

        query = """
            SELECT f.title, f.release_year as year, f.rating
            FROM film AS f
            JOIN film_category AS fc ON f.film_id = fc.film_id
            JOIN category AS c ON c.category_id = fc.category_id
            WHERE c.category_id = %s AND f.release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
        """
        return self.paginate(
            query=query, params=(genre_id, start, end), total_count=films_count
        )

    def search_by_rating_year(self, rating, films_count, start, end):
        if films_count == 0:
            return

        query = """
            SELECT f.title, f.release_year as year, c.name AS genre
            FROM film AS f
            JOIN film_category AS fc ON f.film_id = fc.film_id
            JOIN category AS c ON c.category_id = fc.category_id
            WHERE f.rating = %s AND f.release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
        """
        return self.paginate(
            query=query, params=(rating, start, end), total_count=films_count
        )

    def __del__(self):
        if self.connection.open:
            self.connection.close()
