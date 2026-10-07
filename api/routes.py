from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.ticket_service import transition_ticket, TransitionError

api_bp = Blueprint('api', __name__)


@api_bp.route('/tickets/<int:ticket_id>/transition', methods=['POST'])
@login_required
def ticket_transition(ticket_id):
    data = request.get_json() or {}
    target_status = data.get('target_status')
    remark = data.get('remark')
    expected_version = data.get('version')

    try:
        transition_ticket(ticket_id, target_status, operator=current_user, remark=remark, expected_version=expected_version)
    except TransitionError as e:
        return jsonify(code=409, message=str(e)), 409

    return jsonify(code=0, message='success')
