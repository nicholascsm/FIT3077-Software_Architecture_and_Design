import os
from flask import Flask
from online_matching_system.config import Config
import sys

# to stop python from writing bytecode files
sys.dont_write_bytecode = True

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from online_matching_system.users.routes import users
    from online_matching_system.bids.routes import bids
    from online_matching_system.main.routes import main
    from online_matching_system.contract.routes import contracts
    app.register_blueprint(users)
    app.register_blueprint(bids)
    app.register_blueprint(main)
    app.register_blueprint(contracts)

    return app
