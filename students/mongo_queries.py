# # mongo_queries.py

# from pymongo import MongoClient
# import base64
# from bson.binary import Binary
# from students.models import Student
# from django.core.files.uploadedfile import InMemoryUploadedFile

# def handle_photo_upload(studentid, photo_file):
#     student = Student.objects.get(pk=studentid)
   
#     # Ensure photo_file is InMemoryUploadedFile
#     if isinstance(photo_file, InMemoryUploadedFile):
#         # Convert the image file to binary
#         encoded_image = base64.b64encode(photo_file.read())
    
#         # Connect to MongoDB
#         client = MongoClient('mongodb://localhost:27017/')
#         db = client['myschool']
#         collection = db['student_photos']

#         result = collection.insert_one({
#             'student_id':  student.studentid,
#             'photo_data': Binary(encoded_image),
#             'content_type': 'image/jpeg'  # Adjust as per your image type
#         })

#         # Close MongoDB connection
#         client.close()

#         return str(result.inserted_id)  # Return MongoDB photo ID as string
#     else:
#         raise ValueError("Invalid file type. Expected InMemoryUploadedFile.")
    

# def retrieve_photo(photo_id):
#     # Connect to MongoDB
#     client = MongoClient('mongodb://localhost:27017/')
#     db = client['myschool']
#     collection = db['student_photos']
    
#     # Retrieve the photo data
#     photo_data = collection.find_one({'_id': photo_id})
    
#     # Close MongoDB connection
#     client.close()
    
#     if photo_data:
#         return base64.b64encode(photo_data['photo_data']).decode('utf-8')  # Return the Base64 encoded photo data
#     else:
#         raise ValueError("Photo not found.")
 




from pymongo import MongoClient
import base64
from bson import Binary, ObjectId
from students.models import Student
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime, timedelta

# MongoDB Configuration
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'myschool'

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
photo_collection = db['student_photos']
document_collection = db['student_documents']

# Handling Photo Upload
def handle_photo_upload(studentid, photo_file):
    student = Student.objects.get(pk=studentid)
   
    # Ensure photo_file is InMemoryUploadedFile
    if isinstance(photo_file, InMemoryUploadedFile):
        # Convert the image file to binary
        encoded_image = base64.b64encode(photo_file.read())
    
        result = photo_collection.insert_one({
            'student_id':  student.studentid,
            'photo_data': Binary(encoded_image),
            'content_type': 'image/jpeg'  # Adjust as per your image type
        })

        return str(result.inserted_id)  # Return MongoDB photo ID as string
    else:
        raise ValueError("Invalid file type. Expected InMemoryUploadedFile.")
    
# Retrieving Photo
def retrieve_photo(photo_id):
    # Retrieve the photo data
    photo_data = photo_collection.find_one({'_id': ObjectId(photo_id)})
    
    if photo_data:
        return base64.b64encode(photo_data['photo_data']).decode('utf-8')  # Return the Base64 encoded photo data
    else:
        raise ValueError("Photo not found.")

# Uploading Document
def upload_document(studentid, document_file):
    student = Student.objects.get(pk=studentid)
    
    # Ensure document_file is InMemoryUploadedFile
    if isinstance(document_file, InMemoryUploadedFile):
        # Convert the document file to binary
        file_data = document_file.read()

        result = document_collection.insert_one({
            'student_id': student.studentid,
            'document_name': document_file.name,
            'document_data': Binary(file_data),
            'content_type': document_file.content_type,
            'upload_date': datetime.utcnow()  # Add upload date
        })

        return str(result.inserted_id)  # Return MongoDB document ID as string
    else:
        raise ValueError("Invalid file type. Expected InMemoryUploadedFile.")

# Retrieving Documents from Last 3 Months
def get_recent_documents(studentid):
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    
    documents = document_collection.find({
        'student_id': studentid,
        'upload_date': {'$gte': three_months_ago}
    })
    
    return [{
        'document_id': str(doc['_id']),
        'document_name': doc['document_name'],
        'upload_date': doc['upload_date']
    } for doc in documents]

