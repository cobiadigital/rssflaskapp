from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import datetime
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from podcast.auth import login_required
from podcast.db import get_db
import os
from mutagen.mp3 import MP3

bp = Blueprint('feed', __name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp3'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, created, title, description, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('feed/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        guid = request.form['guid']
        audio_file = request.files['audio_file']
        if audio_file and allowed_file(audio_file.filename):
            audiofilename = secure_filename(audio_file.filename)
            audio_file.save(os.path.join('/Users/Ben/pythonProject/rssapp/static/audio/', audiofilename))
            audio_size = os.stat(os.path.join('/Users/Ben/pythonProject/rssapp/static/audio/', audiofilename)).st_size


        audio = MP3(audio_file)
        audio_file_length = str(datetime.timedelta(seconds=round(audio.info.length)))
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, description, guid, audiofilename, audio_size, audio_file_length, author_id)'
                ' VALUES (?,?,?,?,?,?,?)',
                (title, description, guid, audiofilename, audio_size, audio_file_length, g.user['id'],)
            )
            db.commit()
            return redirect(url_for('feed.index'))

    return render_template('feed/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, description, guid, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        guid = request.form['guid']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, description = ?, guid = ?'
                ' WHERE id = ?',
                (title, description, guid, id,)
            )
            db.commit()
            return redirect(url_for('feed.index'))
    return render_template('feed/update.html', post=post)


@bp.route('/rss')
def rss():
    """Generate rss feed."""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, created, title, description, author_id, username, audiofilename, audio_file_length, audio_size, guid'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('feed/rss_feed.html', posts=posts)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('feed.index'))
