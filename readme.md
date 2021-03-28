# Candy Shop
## About
This is a demonstration project that implements the API for a candy delivery service.

The full API description can be found in openapi.yaml.

## Dependencies
### Development 
1. PostgreSQL (any modern version higher than v9)
2. Python (3.6 or higher)
3. Python packages listed in requirements.txt

### Deployment
All the dependencies listed in the section above, plus:
1. Gunicorn (any modern version)
2. Supervisor (any modern version)

## Installation
### Development
1. Follow the link to install PostgreSQL: https://www.postgresql.org/download/
2. Install Python 3 and create virtualenv.
   The recommended way is to use pyenv (https://github.com/pyenv/pyenv).
3. While being in the project root and having venv activated, install required python packages:

   `pip install -r requirements.txt`

4. Create and edit local.py in candy_shop/settings/ using local.example.py.
   You may also want to turn on the debug mode `DEBUG=True`.
5. Create the user and the database according to your settings, e.g.:

   `postgres=# CREATE USER candy_shop WITH PASSWORD 'candy_shop';`

   `postgres=# ALTER USER candy_shop CREATEDB;`

   `postgres=# CREATE DATABASE candy_shop;`

   `postgres=# ALTER DATABASE candy_shop OWNER TO candy_shop;`
6. Run migrations:

    `./manage.py migrate`

7. Start server:

   `./manage.py runserver`

8. To run tests use the command:

   `./manage.py test`
### Deployment
Follow the instructions given in the section above with a few caveats:
- Don't use simple passwords
- Don't use the debug mode (DEBUG setting should be always False).

Then:
1. Install supervisor (http://supervisord.org/installing.html)
2. To run supervisor without sudo, open the config file:

   `sudo vim /etc/supervisor/supervisord.conf`

3. Under the `[unix_http_server]` section add the string:

   `chown=youruser:yourgroup`

4. Restart the supervisor:

   `sudo systemctl restart supervisor`

5. Add create the configuration file for this project inside the supervisor/conf.d
   directory:

   `sudo vim /etc/supervisor/conf.d/candy_shop.conf`

6. An example of the candy_shop.conf:

   `[program:candy_shop]`
   
   `command=/home/youruser/.pyenv/versions/candy-shop-3.9.1/bin/gunicorn -w 9 -b 0.0.0.0:8080 candy_shop.wsgi`
   
   `directory=/home/youruser/projects/candy_shop/candy_shop`
   
   `user=youruser`
   
   `autostart=true`

   `autorestart=true`

   `redirect_stderr=true`

   `stdout_logfile=/home/youruser/projects/candy_shop/logs/gunicorn.log`

7. Make the config visible for supervisor:

   `supervisorstl reread`

8. Start the service:

   `supervisorctl start candy_shop`
