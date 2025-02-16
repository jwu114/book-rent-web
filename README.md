# Unibook Website
This is an in-class project for CSC 210 - Web Programming at the University of Rochester. It is a locally operable prototype of a web app designed for renting books.

## How to Run
### Initialize Database
Enter the following codes:
```
flask --app flasky shell
from app import db
from app.models import init_books
db.drop_all()
db.create_all()
init_books()
quit()
```

### Run Program
Enter the following codes:
```
flask --app flasky run
```



    
    
