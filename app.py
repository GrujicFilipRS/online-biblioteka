from flask import Flask, render_template, redirect, render_template, redirect, request, render_template_string, g
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.books import Book
from data.users import User
from data.authors import Author
from forms.search import SearchForm
from forms.user import UserSignInForm, UserSignUpForm

from datetime import datetime, timedelta
from tools.nlp import tokenize

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

app.book_index = {}
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
HOST = '127.0.0.1'
PORT = 8080


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.before_request
def handle_search():
    g.search_form = SearchForm()
    if g.search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{g.search_form.search.data}")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login')
def login_page():
    return render_template('login.html', title='Log in')

    sign_in_form = UserSignInForm()
    if sign_in_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == sign_in_form.email.data).first()
        if user and user.check_password(sign_in_form.password.data):
            login_user(user, remember=sign_in_form.remember_me.data)
            return redirect('/')
        return render_template(
            "sign_in_user.html",
            title="Sign In",
            message="Incorrect email or password",
            sign_in_form=sign_in_form,
            search_form=g.search_form
        )
    return render_template(
        "sign_in_user.html",
        title="Sign In",
        sign_in_form=sign_in_form,
        search_form=g.search_form
    )


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    sign_up_form = UserSignUpForm()
    if sign_up_form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == sign_up_form.email.data).first() is not None:
            return render_template(
                "sign_up_user.html",
                title="Sign In",
                search_form=g.search_form,
                message="There is already an account with that email!",
                sign_up_form=sign_up_form
            )
        if db_sess.query(User).filter(User.nickname == sign_up_form.nickname.data).first() is not None:
            return render_template(
                "sign_up_user.html",
                title="Sign In",
                search_form=g.search_form,
                message="There is already an account with that nickname!",
                sign_up_form=sign_up_form
            )
        user = User(
            email=sign_up_form.email.data,
            nickname=sign_up_form.nickname.data,
            age=sign_up_form.age.data,
            description=sign_up_form.description.data,
        )
        user.set_password(sign_up_form.password.data),
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template(
        "sign_up_user.html",
        title="Sign Up",
        search_form=g.search_form,
        sign_up_form=sign_up_form
    )


@app.route('/search/<string:search>', methods=["GET", "POST"])
def search(search_text: str):
    ids = []
    search_token = tokenize(search_text)
    for article_id, book_token in app.book_index.items():
        num_matching_words = len(search_token & book_token)
        if num_matching_words > 0:
            ids.append((article_id, num_matching_words))
    ids.sort(key=lambda x: x[1], reverse=True)
    ids = [i[0] for i in ids]

    sess = db_session.create_session()
    articles = sess.query(Book).filter(Book.id.in_(ids)).all()
    return render_template("search_results.html", articles=articles, search_form=g.search_form)


# Za vreme testiranja, vratiti kad bude gotovo
@app.route('/library', methods=["GET", "POST"])
def library():
    return render_template('book.html', title='Knjiga')


@app.route('/library/<string:book_id>', methods=["GET", "POST"])
def library_book(book_id: str):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book is None:
        return render_template("book.html",
                               answer=False,
                               search_form=g.search_form)
    book_dict = {
        "id": book.id,
        "title": book.title,
        "uploaded_user_id": book.uploaded_user_id,
        "created_at": book.created_at,
        "author_id": book.author_id,
        "description": book.description
    }
    return render_template("book.html",
                           answer=True,
                           book=book_dict,
                           search_form=g.search_form)


@app.route('/')
def index():
    return render_template("index.html", title="Library", search_form=g.search_form)


def main() -> None:
    db_session.global_init("db/library.sqlite")
    sess = db_session.create_session()
    books = sess.query(Book).all()
    for book in books:
        app.book_index[book.id] = tokenize(book.title)
    app.run(host=HOST, port=PORT, debug=True, threaded=True)


if __name__ == "__main__":
    main()
