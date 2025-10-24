# mongodb_manager.py
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from dateutil import parser as date_parser
import os

MONGO_URI = "mongodb+srv://decry:%40Cdc90c8@clusterdecry.8qg1dz6.mongodb.net/?appName=ClusterDecry"
DB_NAME = os.getenv("MONGODB_DB", "school_db")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "students")

class MongoDBManager:
    def __init__(self, uri=MONGO_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Force connection on init
            self.client.server_info()
            self.db = self.client[db_name]
            self.col = self.db[collection_name]
        except errors.ServerSelectionTimeoutError as e:
            raise ConnectionError(f"Não foi possível conectar ao MongoDB: {e}")

    def create_student(self, student_data: dict):
        """student_data: dict com keys: name, birthdate (YYYY-MM-DD), email, course, enrollment_number"""
        doc = student_data.copy()
        # normalize birthdate to ISO format string
        if "birthdate" in doc and doc["birthdate"]:
            try:
                dt = date_parser.parse(doc["birthdate"])
                doc["birthdate"] = dt.date().isoformat()
            except Exception:
                raise ValueError("Formato de data inválido. Use YYYY-MM-DD.")
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def list_students(self):
        docs = list(self.col.find())
        return [self._doc_to_dict(d) for d in docs]

    def get_student(self, student_id: str):
        try:
            oid = ObjectId(student_id)
        except Exception:
            return None
        doc = self.col.find_one({"_id": oid})
        return self._doc_to_dict(doc) if doc else None

    def update_student(self, student_id: str, updates: dict):
        try:
            oid = ObjectId(student_id)
        except Exception:
            return False
        if "birthdate" in updates and updates["birthdate"]:
            try:
                updates["birthdate"] = date_parser.parse(updates["birthdate"]).date().isoformat()
            except Exception:
                raise ValueError("Formato de data inválido. Use YYYY-MM-DD.")
        result = self.col.update_one({"_id": oid}, {"$set": updates})
        return result.modified_count > 0

    def delete_student(self, student_id: str):
        try:
            oid = ObjectId(student_id)
        except Exception:
            return False
        result = self.col.delete_one({"_id": oid})
        return result.deleted_count > 0

    def _doc_to_dict(self, doc):
        if not doc:
            return None
        d = dict(doc)
        d["id"] = str(d.pop("_id"))
        # ensure birthdate is string (already stored as ISO string)
        if "birthdate" in d and d["birthdate"] is not None:
            d["birthdate"] = str(d["birthdate"])
        return d