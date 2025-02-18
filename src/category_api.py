from flask import Blueprint, request, jsonify
from models import db, Category

category_bp = Blueprint("category_bp", __name__)

@category_bp.route("/", methods=["GET"])
def get_categories():
    """Retrieve all categories."""
    categories = Category.query.all()
    return jsonify([
        {"name": cat.name, "description": cat.description} for cat in categories
    ]), 200

@category_bp.route("/<string:name>", methods=["GET"])
def get_category(name):
    """Retrieve a single category."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({
        "name": category.name,
        "description": category.description
    }), 200

@category_bp.route("/", methods=["POST"])
def create_category():
    """Create a new category."""
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Missing category name"}), 400

    category = Category(name=data["name"], description=data.get("description"))
    db.session.add(category)

    try:
        db.session.commit()
        return jsonify({"message": "Category created successfully"}), 201
    except:
        db.session.rollback()
        return jsonify({"error": "Category already exists"}), 409

@category_bp.route("/<string:name>", methods=["PUT"])
def update_category(name):
    """Update a category's description."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.json
    category.description = data.get("description", category.description)
    db.session.commit()
    return jsonify({"message": "Category updated"}), 200

@category_bp.route("/<string:name>", methods=["DELETE"])
def delete_category(name):
    """Delete a category."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200
