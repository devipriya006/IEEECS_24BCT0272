import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    # Set this to your MongoDB Atlas connection string or use local if testing
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cinepass")
