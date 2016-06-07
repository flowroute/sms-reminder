import json

from celery import Celery
from flask import Flask


def new_celery(app):
    celery = Celery(app.name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERY_IMPORTS=("tasks",),
)

celery = new_celery(app)


@celery.task
def add_together(a, b):
    return a + b


@app.route('/', methods=['POST'])
def addition():
    task = add_together.apply_async(args=[3, 4])
    while task.state == 'PENDING':
        print('Pending')

    return json.dumps({'result': task.info})


if __name__ == '__main__':
    app.run(debug=True)
