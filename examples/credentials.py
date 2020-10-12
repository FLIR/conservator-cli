from conservator import Credentials

# The first time you run this, you will need to input your credentials.
c = Credentials.default()
print(c)
# But then we save them.
c.save_to_default_config()

# This won't prompt for credentials, they've been automatically loaded
# from your config file (that we just saved to).
new_c = Credentials.default()
print(c)
assert c == new_c


