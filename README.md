# work-timer
![penguin meme](https://raw.githubusercontent.com/beebeebop/work-timer/master/web/project/static/cards/card_0_azenx.jpg)


This is a timer that runs in the browser. It tracks your working hours and plots figures to show the amount of time that you spent on each task. For more usage information, check out this blog:  [Lost Track of Your Hours, Days, Life? Try This Simple Timer App](https://blog.beebeebop.com/timer)

This web application is built with Flask and Python.
Data is stored in sqlite3 with the help of Flask-SQLAlchemy and Flask-Migrate
Web forms are built with WTForms, Flask-Bootstrap and Flask-WTF
Figures are rendered with Matplotlib + mpld3 
The timer is in Javascript, which is largely borrowed from [github.com/helloflask/timer](https://github.com/helloflask/timer)
The application is containerized with Docker

Here is a demo: [timer.beebeebop.com](https://timer.beebeebop.com)




## To run the service

### With docker:
Pull the image from docker hub: 
```
$ docker pull beebeebop/work-timer
$ docker run -dit -p 80:8000 --name work-timer-1 --volume=<a directory on host machine>:/home/flask/app/web/instance/dbfiles beebeebop/work-timer /usr/local/bin/gunicorn -w 2 -b :8000 project.wsgi:app
```
or to build the docker image from source:
```
$ cd web
$ docker build -t work-timer .
$ docker run -dit -p 80:8000 --name work-timer-1 --volume=<a directory on host machine>:/home/flask/app/web/instance/dbfiles work-timer:latest /usr/local/bin/gunicorn -w 2 -b :8000 project.wsgi:app
```

If running for the first time, do the following to create the database file:
```
$ docker exec -it work-timer-1 bash -c "export FLASK_APP=run.py && flask db upgrade"
```



### With docker-compose:
```
$ docker-compose -f docker-compose-dev.yml build
$ docker-compose -f docker-compose-dev.yml up -d
```

If running for the first time, do the following to create the database file:
```
$ docker-compose -f docker-compose-dev.yml run --rm web bash
$ export FLASK_APP=run.py
$ flask db upgrade                         
```


### With virtualenv:
```
$ mkvirutalenv work-timer -p python3
$ pip install -r requirements.txt
$ cd web
$ python run.py
```
or
```
$ export FLASK_APP=run.py
$ flask run
```

If running for the first time, do the following to create the database file:
```                 
$ flask db upgrade                 
```




## Background Images
You can customize the background images of the timer to whatever you like. The current ones are generated from [app.beebeebop.com](https://app.beebeebop.com)

For now, you do have to update the code to change the background images but I plan to make this easier.




## Important!
Don't forget to change the SECRET_KEY in flask.cfg if you are deploying this service in WAN. 


