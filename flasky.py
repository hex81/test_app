#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Create by hex7 at 11/22/18
#

from app import create_app, db
from app.models import TRTFailedRecord
from flask_migrate import Migrate

app = create_app('production')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=TRTFailedRecord)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9000', debug=True, use_reloader=True)
