from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from extensions import mongo  # Make sure extensions.py defines: mongo = PyMongo()

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/api/admin/pending_owners', methods=['GET'])
def pending_owners():
    # Fetch all users with role "owner" and approved flag False
    pending = list(mongo.db.users.find({"role": "owner", "approved": False}))
    for owner in pending:
        owner['_id'] = str(owner['_id'])
    return jsonify(pending)

@admin_routes.route('/api/admin/approve_owner', methods=['POST'])
def approve_owner():
    data = request.json
    owner_id = data.get('owner_id')
    if not owner_id:
        return jsonify({'error': 'Owner ID required'}), 400

    result = mongo.db.users.update_one(
        {"_id": ObjectId(owner_id), "role": "owner"},
        {"$set": {"approved": True}}
    )
    if result.modified_count == 1:
        return jsonify({'message': 'Owner approved successfully!'}), 200
    else:
        return jsonify({'error': 'Approval failed'}), 400
