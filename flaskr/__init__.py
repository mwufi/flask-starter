import os
from flask import Flask, render_template

DB_FILE = "/Users/aii/04_Hacks/blobbo/sync-server/test.db"

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_FILE}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # load up more configs!!
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # ok, now we're done with config
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # DB!!
    from . import db
    db.init_app(app)

    # Routes!
    from . import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')

    # now, routes and stuff!
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route('/')
    def index():
        return render_template('index.html')
        

    return app
    
    