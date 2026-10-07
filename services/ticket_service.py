from sqlalchemy import update
from extensions import db
from models import Ticket, TicketOperationLog

ALLOWED_TRANSITIONS = {
    '待处理': ['处理中'],
    '处理中': ['已解决'],
    '已解决': ['已关闭'],
    '已关闭': []
}


class TransitionError(Exception):
    pass


def transition_ticket(ticket_id, target_status, operator=None, remark=None, expected_version=None):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        raise TransitionError('ticket not found')

    current_status = ticket.status
    if target_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise TransitionError(f'invalid transition {current_status} -> {target_status}')

    stmt = (
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .where(Ticket.version == (expected_version if expected_version is not None else ticket.version))
        .values(status=target_status, version=Ticket.version + 1, updated_at=db.func.now())
    )
    result = db.session.execute(stmt)
    if result.rowcount != 1:
        db.session.rollback()
        raise TransitionError('conflict: ticket modified by another user')

    log = TicketOperationLog(
        ticket_id=ticket_id,
        operator_id=getattr(operator, 'id', None),
        action='transition',
        from_status=current_status,
        to_status=target_status,
        remark=remark,
    )
    db.session.add(log)
    db.session.commit()
    return True
