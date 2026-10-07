from celery_app import celery


@celery.task(name='export_ticket_excel')
def export_ticket_excel(params, user_id):
    return {'status': 'ok', 'params': params, 'user_id': user_id}


@celery.task(name='send_ticket_notification')
def send_ticket_notification(ticket_id, event):
    return {'status': 'ok', 'ticket_id': ticket_id, 'event': event}


@celery.task(name='classify_ticket_with_llm')
def classify_ticket_with_llm(ticket_id):
    return {'status': 'ok', 'ticket_id': ticket_id}
