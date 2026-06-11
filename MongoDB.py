from pymongo import MongoClient
from datetime import datetime


class MongoDB:
    def __init__(self, mongoconfig):
        self.client = MongoClient(mongoconfig)
        self.client.admin.command("ping")
        self.db = self.client["ich_edit"]
        self.coll = self.db["final_project_dam281125_KoniievaS"]

    def save_log(self, search_type, params, results_count):
        """
        Saves successful user search requests to MongoDB.

        Creates a document containing search type, search parameters,
        number of found films, and search timestamp.
        """
    
        document = {
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
            "search_time": datetime.now(),
        }

        self.coll.insert_one(document)

    def get_top_searches(self, search_type):
        """
        Returns the top 5 most popular search requests by search type.

        Uses MongoDB aggregation to group requests, count how often each
        request was used, and sort results by popularity and last search time.
        """
        
        if search_type == "keyword":
            group_id = "$params.keyword"
            project = {"_id": 0, "count": 1, "keyword": "$_id", "results_count": 1}
        elif search_type == "genre & year":
            group_id = {
                "genre_name": "$params.genre_name",
                "start_year": "$params.start_year",
                "end_year": "$params.end_year",
            }
            project = {
                "_id": 0,
                "count": 1,
                "genre": "$_id.genre_name",
                "start_year": "$_id.start_year",
                "end_year": "$_id.end_year",
                "results_count": 1,
            }
        elif search_type == "rating":
            group_id = {
                "rating": "$params.rating",
                "start_year": "$params.start_year",
                "end_year": "$params.end_year",
            }
            project = {
                "_id": 0,
                "count": 1,
                "rating": "$_id.rating",
                "start_year": "$_id.start_year",
                "end_year": "$_id.end_year",
                "results_count": 1,
            }

        pipeline = [
            {"$match": {"search_type": search_type}},
            {
                "$group": {
                    "_id": group_id,
                    "count": {"$sum": 1},
                    "results_count": {"$first": "$results_count"},
                    "last_search_time": {"$max": "$search_time"},
                }
            },
            {"$project": project},
            {"$sort": {"count": -1, "last_search_time": -1}},
            {"$limit": 5},
        ]

        return list(self.coll.aggregate(pipeline))

    def get_last_searches(self, limit=5):
        """
        Returns the last unique search requests.

        Uses MongoDB aggregation to group identical requests and keep only
        the most recent search time for each unique request.
        """
        
        pipeline = [
            {"$sort": {"search_time": -1}},
            {
                "$group": {
                    "_id": {"search_type": "$search_type", "params": "$params"},
                    "last_search_time": {"$first": "$search_time"},
                    "results_count": {"$first": "$results_count"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "search_type": "$_id.search_type",
                    "params": "$_id.params",
                    "results_count": 1,
                    "last_search_time": 1,
                }
            },
            {"$sort": {"last_search_time": -1}},
            {"$limit": limit},
        ]
        return list(self.coll.aggregate(pipeline))

    def __del__(self):
        self.client.close()
