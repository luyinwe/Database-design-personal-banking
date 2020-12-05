# Database-design-personal-banking
Use Django and html to design a webpage



## Data Preparation and Setup

1. Which database system(s) and version(s) are you using? How do we install it/them?

> SQLite3.  Download from https://www.sqlite.org/index.html

2. How do we download the data you used for your project? Please do NOT submit ALL the data with your code (Submitting a very small portion (< 5 MB) so that we can run the demo might be okay)

> The data is in the file ./personalbank/db.sqlite3. It is only about 4MB.

3. How do we load this data into the database system? 

> You only need to run the scripts. You need to install python3 and all the libraries required. Then open cmd and type in:

```python
python manage.py runserver
```

> Then open a browser and type in:

```
http://localhost:8000/
```

> In this page you can do all the operations.

> To check all the information in the database, you should get an administration account. Open another browser and type in:

```
http://localhost:8000/admin
```

> The admin username is 'admin', password is '123456'.

> Or you can create a new superuser(administrator) by:

```python
python manage.py create superuser
```

4. If you are generating your own data, how do we generate it? 

   > I use a python library named faker. You can install it by:

   ```python
   pip install faker
   ```

   

   ## Application and code

   1. Which programming language(s) and version(s) are you using (Python, Java 8, C++, etc.)?

      > python 3

   2. List the third-party libraries needed to execute your code and how do we install them (For ex. MySQL/neo4j connector for Python)

      > Use command "pip install django, faker, time, numpy". If there needs other libraries, please install them with the same format.  

   3. If you have a GUI, how do we run it?

      > After you run the script by "python manage.py runserver", you can open a browser and type in "http://localhost:8000" and "http://localhost:8000/admin"

   4. Anything else we need to know about running your application?

      > please get information from admin panel and use the information to make user login and operator login.

   ## Code Documentation and References

   1. Did you use some code from GitHub or other sources? If yes provide the link.

      > I didn't use the code from Github sources. But I use the guide of Django
      >
      > "https://docs.djangoproject.com/en/3.1/intro/tutorial01/"

      

   2. Give a list of files in your submission which are written by you.

      ```
      /personalbank/banking/templates
      /personalbank/banking/views.py
      /personalbank/banking/urls.py
      /personalbank/banking/models.py
      /personalbank/personalbank/urls.py
      /personalbank/populate_script.py
      ```

      