from app import app, mongo

def initialize_db():
    with app.app_context():
        # Create unique indexes for users
        mongo.db.users.create_index("username", unique=True)
        mongo.db.users.create_index("email", unique=True)
        print("Database initialized with unique indexes.")

if __name__ == '__main__':
    initialize_db()
