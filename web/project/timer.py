import functools
from datetime import datetime
import pytz
import random

from flask import Blueprint, render_template, g, session, redirect, url_for, flash, request, abort, jsonify

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, RadioField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp, ValidationError, NumberRange

#For simple data processing
import numpy as np


#For plotting
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mpld3

from project import db
from project.models import User, Tag, Work


bp = Blueprint('timer', __name__, )


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("timer.login"))

        return view(**kwargs)

    return wrapped_view


#--------------------------------show stats--------------------------------------
@bp.route("/stats/tag/<tagname>", methods=["GET"])
@login_required
def tag_stats(tagname):

    tag = Tag.get_tag_by_name(tagname, g.user)
    if tag is None:
        abort(400, "You don't have tag: ".format(tagname))
    else:
        tt, vv = get_tag_data(tag, duration='day')
        tt_w, vv_w = get_tag_data(tag, duration='week')
        tt_m, vv_m = get_tag_data(tag, duration='month')

        fig = Figure(figsize=(10,7.5))
        fig.subplots_adjust(hspace = 0.4)
        ax = fig.add_subplot(3, 1, 1)
        ax.step(tt, vv, where='post', label=tagname)
        ax.legend(loc='upper right', shadow=True)
        ax.set_xlabel('hour')
        ax.set_title('Work Time')

        ax = fig.add_subplot(3, 1, 2)
        ax.step(tt_w/24, vv_w, where='post', label=tagname)
        ax.legend(loc='upper right', shadow=True)
        ax.set_xlabel('day')


        ax = fig.add_subplot(3, 1, 3)
        ax.step(tt_m/24, vv_m, where='post', label=tagname)
        ax.legend(loc='upper right', shadow=True)
        ax.set_xlabel('day')


        html_text = mpld3.fig_to_html(fig)
        return html_text

def get_tag_data(tag, duration='day'):
    display_end = datetime.utcnow()
    display_end_in_unixtime_sec = datetime_to_unixtime(display_end)
    if duration=='day':
        display_start_in_unixtime_sec = display_end_in_unixtime_sec - 24*60*60
    elif duration=='week':
        display_start_in_unixtime_sec = display_end_in_unixtime_sec - 7*24*60*60
    elif duration=='month':
        display_start_in_unixtime_sec = display_end_in_unixtime_sec - 30*24*60*60
    else:
        raise Exception('get_tag_data(): duration not supported.')
    display_start = unixtime_to_datetime(display_start_in_unixtime_sec*1000)

    #for now, assume work session of one tag have no overlap, although this is not guaranteed
    works = Work.query.filter_by(tag_id=tag.id).filter(Work.start_time > display_start).filter(Work.end_time < display_end).order_by(Work.start_time).all()


    t = [display_start_in_unixtime_sec]
    v = [0]

    for work in works:
        t1 = datetime_to_unixtime(work.start_time)
        t2 = datetime_to_unixtime(work.end_time)
        t.append(t1)
        v.append(1)
        t.append(t2)
        v.append(0)
    t.append(display_end_in_unixtime_sec)
    v.append(0)

    tt = np.array(t)
    vv = np.array(v)
    tt = tt/(60*60) #into hour
    tt = tt - tt[-1]

    return tt, vv



@bp.route("/stats/bar", methods=["GET"])
@login_required
def stats():
    #need options to provide, last 24 hour, last 2 days, last week, last month
    display_end = datetime.utcnow()
    display_end_in_unixtime_sec = datetime_to_unixtime(display_end)
    display_start_in_unixtime_sec = display_end_in_unixtime_sec - 24*60*60
    display_start = unixtime_to_datetime(display_start_in_unixtime_sec)


    tags = g.user.tags

    v = []
    for tag in tags:
        #for now, assume work session of one tag have no overlap, although this is not guaranteed
        works = Work.query.filter_by(tag_id=tag.id).filter(Work.start_time > display_start).filter(Work.end_time < display_end).order_by(Work.start_time).all()

        total = 0
        for work in works:
            t1 = datetime_to_unixtime(work.start_time)
            t2 = datetime_to_unixtime(work.end_time)
            total += (t2 - t1)/(60*60)

        v.append(total)

    tagnames = [tag.tagname for tag in tags]
    fig = Figure(figsize=(20,5))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(np.arange(len(tagnames))+1, v, tick_label=tagnames)
    ax.set_title('Work Time')
    ax.set_ylabel('hours')

    html_text = mpld3.fig_to_html(fig)
    return html_text







#---------------------------------timer-------------------------------------------


@bp.route("/timer/set", methods=["GET", "POST"])
@login_required
def set_timer():
    class TimerForm(Form):
        duration = StringField('Duration', validators=[DataRequired(),
                                                        Regexp('\d+[smh]?$', message="Please enter a valid duration such as 34、20s、15m and 2h. ")
                                                    ])
        submit = SubmitField('Start')

    form = TimerForm()
    if form.validate_on_submit():
        d_string = form.duration.data.strip()
        if d_string[-1] not in 'smh':
            session['duration'] = int(d_string)
        elif d_string[-1] is 's':
            session['duration'] = int(d_string[:-1])
        elif d_string[-1] is 'm':
            session['duration'] = int(d_string[:-1])*60
        elif d_string[-1] is 'h':
            session['duration'] = int(d_string[:-1])*60*60

        return redirect(url_for('timer.timer'))

    tagname = request.args.get('tagname', None)
    session['tagname'] = tagname


    return render_template('set_timer.html', form=form)


@bp.route("/timer", methods=["GET"])
@login_required
def timer():
    if 'tagname' not in session:
        redirect(url_for('timer.showtags'))
    else:
        card = random.choice('card_0_azenx.jpg  card_1_ddlky.jpg  card_1_sorlt.jpg  card_3_ksseo.jpg  card_4_llkof.jpg  card_6_optcc.jpg  card_8_gtfqy.jpg  card_9_hvrtw.jpg  card_9_rkaio.jpg  card_0_azlat.jpg  card_1_juqar.jpg  card_2_nrmrw.jpg  card_3_qtiqi.jpg  card_5_wbyup.jpg  card_6_xtjal.jpg  card_8_pvxrf.jpg  card_9_jluxu.jpg  card_9_viyna.jpg  card_0_rselx.jpg  card_1_likng.jpg  card_3_cqgxc.jpg  card_4_bbgdi.jpg  card_6_nhbfk.jpg  card_7_upeoc.jpg  card_8_yiezz.jpg  card_9_ogqkr.jpg'.split())
        return render_template('timer.html', card=card)



@bp.route("/session/add", methods=["POST"])
@login_required
def add_session():
    start = request.args.get('start', None, type=int)
    end = request.args.get('end', None, type=int)

    #print(start)
    #print(end)
    start_datetime = unixtime_to_datetime(start)
    end_datetime = unixtime_to_datetime(end)

    tag = Tag.get_tag_by_name(session['tagname'], g.user)
    if tag is not None:
        new_work = Work(start_datetime, end_datetime, tag)
        db.session.add(new_work)
        db.session.commit()
    else:
        abort(400, "You don't have tag: ".format(session['tagname']))

    response = jsonify({'result':'done'})
    response.status_code = 201
    return response


#--------------------------------user tags--------------------------------------

@bp.route("/tags/show", methods=["GET"])
@login_required
def showtags():
    tags = g.user.tags.all()
    return render_template('show_tags.html', tags = tags)



@bp.route("/tag/create", methods=["GET", "POST"])
@login_required
def create_tag():
    class TagForm(Form):
        tag = StringField('Tag', validators=[DataRequired()])
        submit = SubmitField('Submit')

    form=TagForm()
    if form.validate_on_submit():
        #should not allow one user to have two identical tags
        if Tag.exist(form.tag.data, g.user):
            abort(400, 'You already have this tag: {}.'.format(form.tag.data))

        new_tag = Tag(form.tag.data, g.user)
        db.session.add(new_tag)
        db.session.commit()

        flash('1 tag added to the database.')
        return redirect(url_for('timer.showtags'))

    return render_template('addtag.html', form=form)




#---------------------------------user login and logout-----------------------------

@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()




@bp.route("/create", methods=["GET", "POST"])
def create():
    class CreateForm(Form):
        username = StringField('User Name', validators=[DataRequired(),
                                                                Regexp('^\w+$', message="User name must contain only letters, numbers or underscore"),
                                                                Length(min=1, max=64, message="User name must be betwen 1 & 64 characters")
                                                                ])
        password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=40, message="Password must be betwen 3 & 40 characters")])
        confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Create')


        def validate_username(self, username):
            #Validates that the user name is not already taken.
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('User "{0}" already exists.'.format(username.data))


    #Create a new user.
    form = CreateForm()
    if form.validate_on_submit():
        #print(form.username.data)
        new_user = User(form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        session.clear()
        session["user_id"] = new_user.id
        return redirect(url_for("timer.showtags", userName=form.username.data))


    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    class LoginForm(Form):
        username = StringField('User Name', validators=[DataRequired(),
                                                            Regexp('^\w+$', message="User name must contain only letters, numbers or underscore"),
                                                            Length(min=1, max=64, message="User name must be betwen 1 & 64 characters")
                                                            ])
        password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=40, message="Password must be betwen 3 & 40 characters")])
        submit = SubmitField('Login')



    #User login
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        error = None
        if user is None:
            error = 'User "{}" does not exist.'.format(form.username.data)
        elif not user.check_password(form.password.data):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("timer.showtags", userName=form.username.data))

        flash(error)

    return render_template("login.html", form=form)





@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("timer.login"))




#--------------------------helper functions------------------------------

#t is int in millisecond
def unixtime_to_datetime(t, tz='UTC'):
    tt = datetime.utcfromtimestamp(int(round(t/1000)))
    utc_aware_tt = tt.replace(tzinfo=pytz.utc)
    return utc_aware_tt.astimezone(pytz.timezone(tz))


def datetime_to_unixtime(t_datetime):
    if t_datetime.tzinfo is not None:
        t_origin = datetime(1970,1,1).replace(tzinfo=pytz.utc)
    else:
        t_origin = datetime(1970,1,1)
    return (t_datetime - t_origin).total_seconds()
