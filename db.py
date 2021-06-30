from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from user import Teacher

client = MongoClient("mongodb+srv://test:test@arson.1khnq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

arson_db = client.get_database("ArsonDb")
teachers_collection = arson_db.get_collection("teachers")


def save_teacher(username, email, password):
    password_hash = generate_password_hash(password)
    teachers_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})


def get_teacher(username):
    teacher_data = teachers_collection.find_one({'_id': username})
    return Teacher(teacher_data['_id'], teacher_data['email'], teacher_data['password']) if teacher_data else None



