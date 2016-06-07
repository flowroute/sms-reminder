import json

from app import app
from tasks import add_together
from database import db_session
from models import Appointment


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/', methods=['POST'])
def addition():
    appt = Appointment('121323', 'foo', 'bar')
    db_session.add(appt)
    db_session.commit()
    task = add_together.apply_async(args=[3, 4])
    while task.state == 'PENDING':
        print('Pending')
    return json.dumps({'result': task.info})


if __name__ == '__main__':
    app.run(debug=True)
