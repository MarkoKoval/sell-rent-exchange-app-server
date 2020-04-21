import bcrypt

password = u'foobar'
password_hashed = bcrypt.hashpw(password, bcrypt.gensalt())