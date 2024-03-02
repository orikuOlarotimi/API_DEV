from flask import Flask
import psycopg
from psycopg.rows import dict_row
from time import sleep
from app import models
from app.database import engine
from app.routers.post import post_bp
from app.routers.user import user_bp
from app.routers.auth import auth_bp


models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(auth_bp)


while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='APi_DEV', user='postgres', password='Dickfish1.',
                               row_factory=dict_row)
        cursor = conn.cursor()
        print("database connection successful")
        break

    except Exception as error:
        print(f"error occured as a result of {error}")
        sleep(2)


@app.route("/")
def greet():
    return {"message": "hello world!"}


if __name__ == '__main__':
    app.run(debug=True)


