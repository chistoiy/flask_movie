from movie import db,create_app

app = create_app()
app_ctx = app.app_context() # app_ctx = film/g
with app_ctx:
    db.create_all()