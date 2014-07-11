from wv import *

def setup_database():
    db.drop_all()
    db.create_all()
    admin = User('Dummy', 'Mr. Dummy', pwd_context.encrypt('dummy'), 'dummy@dummy.com')
    db.session.add(admin)
    db.session.commit()

