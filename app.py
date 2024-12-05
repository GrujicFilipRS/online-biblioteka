from flask import Flask, render_template, redirect, render_template, redirect, request, render_template_string, g, send_from_directory
from flask_login import (LoginManager, login_user,
                         login_required, logout_user, current_user)
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.books import Book
from data.users import User
from data.authors import Author
from forms.search import SearchForm
from forms.user import UserLogInForm, UserSignUpForm

from datetime import datetime, timedelta
from tools.nlp import tokenize

from requests import get as requests_get
import conf.conf as conf
import json

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = conf.SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

app.book_index = {}
app.main_page_books = []
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
    # //made by @yxzhin with <3 03.12.2024. ^^
    # //#hellokittysupremacy #finelcomeback

    if request.path.startswith("/static/"):
        return None

    response = requests_get(
        url="https://api.api-ninjas.com/v1/quotes?category=education",
        headers={"X-Api-Key": conf.API_KEY_QUOTES},
    )

    quote = dict()

    if response.status_code != 200:
        quote["quote"] = "error loading a quote. :( #yxzhinCodeMoment"
        quote["author"] = ""

    quote = json.loads(response.text)[0]
    g.quote = quote

    # //end of my part

    g.search_form = SearchForm()
    if g.search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{g.search_form.search.data}")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = UserLogInForm()
    if login_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.nickname == login_form.nickname.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect('/')
        return render_template(
            "login.html",
            quote=g.quote["quote"],
            author=g.quote["author"],
            title="Log in",
            message="Ne postoji nalog sa takvim mejlom i šifrom",
            login_form=login_form,
            search_form=g.search_form
        )
    return render_template(
        "login.html",
        quote=g.quote["quote"],
        author=g.quote["author"],
        title="Log in",
        login_form=login_form,
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
                quote=g.quote["quote"],
                author=g.quote["author"],
                title="Sign In",
                search_form=g.search_form,
                message="There is already an account with that email!",
                sign_up_form=sign_up_form
            )
        if db_sess.query(User).filter(User.nickname == sign_up_form.nickname.data).first() is not None:
            return render_template(
                "sign_up_user.html",
                quote=g.quote["quote"],
                author=g.quote["author"],
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
        quote=g.quote["quote"],
        author=g.quote["author"],
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
    return render_template("search_results.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           articles=articles,
                           search_form=g.search_form)


# Za vreme testiranja, vratiti kad bude gotovo
@app.route('/library', methods=["GET", "POST"])
def library():
    return render_template(
        'book.html',
        title='Knjiga',
        quote=g.quote["quote"],
        author=g.quote["author"],
    )


@app.route('/library/<string:book_id>', methods=["GET", "POST"])
def library_book(book_id: str):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book is None:
        return render_template("book.html",

                               quote=g.quote["quote"],
                               author=g.quote["author"],

                               answer=False,
                               search_form=g.search_form)
    book_dict = bookToDict(book)
    return render_template("book.html",

                           quote=g.quote["quote"],
                           author=g.quote["author"],

                           answer=True,
                           book=book_dict,
                           search_form=g.search_form)


@app.route('/uploads/books/<filename>')
def serve_pdf(filename):
    return send_from_directory('uploads/books', filename)


@app.route('/')
def index():
    return render_template("index.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           title="Online biblioteka",
                           search_form=g.search_form,
                           books=app.main_page_books)


def addBook(book: dict) -> None:
    db_sess = db_session.create_session()
    author = db_sess.query(Author).filter(
        Author.name == book["author_name"]).first()
    if author is None:
        author = Author(name=book["author_name"])
        db_sess.add(author)

    book = Book(
        title=book["title"],
        uploaded_user_id=1,
        author_id=db_sess.query(Author).filter(
            Author.name == book["author_name"]).first().id,
        path=book["path"],
        description=book["description"],
        year=book["year"],
        grade=book["class"],
    )
    db_sess.add(book)
    db_sess.commit()


def main() -> None:
    db_session.global_init("db/library.sqlite")
    db_sess = db_session.create_session()
    # books = db_sess.query(Book).all()
    # for book in books:
    #    app.book_index[book.id] = tokenize(book.title)

    # getting dicts of 5 books of every grade from 1 to 4
    app.main_page_books = [
        [book.to_dict() for book in db_sess.query(Book).filter(Book.grade == i).limit(5).all()] for i in range(1, 5)
    ]
    app.run(host=HOST, port=PORT, debug=True, threaded=True)


if __name__ == "__main__":
    main()
