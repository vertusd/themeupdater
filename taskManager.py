from celery import Celery

app = Celery('tasks', result_backend = 'db+mysql://my_db_user:Appuser@01@127.0.0.1/task_result_db',\
                      broker='amqp://celeryuser:celery@66.154.105.251:5672/celeryvhost')

@app.task
def add(x, y):
    return x + y

if __name__ == "__main__":
	r = add.apply_async((2, 2))
