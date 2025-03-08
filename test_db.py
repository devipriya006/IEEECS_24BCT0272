from app import mongo

try:
    mongo.db.command("ping")
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
