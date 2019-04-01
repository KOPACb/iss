from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


## from flask import Flask


#app = Flask(__name__)



#if __name__ == '__main__':
#    app.run()
