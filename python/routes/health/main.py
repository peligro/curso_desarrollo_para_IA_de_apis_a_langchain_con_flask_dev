from flask import Blueprint, jsonify
from http import HTTPStatus


health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    return jsonify({"status": "ok"}), HTTPStatus.OK