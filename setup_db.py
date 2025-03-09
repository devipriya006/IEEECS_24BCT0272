from app import app, mongo

def initialize_db():
    with app.app_context():
        mongo.db.users.create_index("username", unique=True)
        mongo.db.users.create_index("email", unique=True)
        mongo.db.movies.create_index("title", unique=False)
        print("Database initialized with unique indexes.")

if __name__ == '__main__':
    initialize_db()
