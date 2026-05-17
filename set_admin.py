from sqlalchemy import create_engine, text
e = create_engine("postgresql://admin:admin_pass@localhost:5432/spacedata")
with e.connect() as c:
    c.execute(text("UPDATE users SET role='admin' WHERE username='admin'"))
    c.commit()
    print("Admin role set!")
