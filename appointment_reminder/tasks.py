from app import celery


@celery.task(name='app.add_together')
def add_together(a, b):
    return a + b
