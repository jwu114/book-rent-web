Unibook Website
Author: Jiarui Wu

- How to initialize database:
$ flask --app flasky shell
from app import db
from app.models import init_books
db.drop_all()
db.create_all()
init_books()
quit()

- How to run the project:
$ flask --app flasky run




    
    
