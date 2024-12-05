from flask import Flask, render_template, redirect, request, g, send_from_directory, flash
from flask_login import (LoginManager, login_user,
                         login_required, logout_user, current_user)
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.books import Book
from data.users import User
from data.authors import Author
from forms.search import SearchForm
from forms.user import UserLogInForm, UserSignUpForm
from forms.book import AddBookForm, EditBookForm

from datetime import timedelta
import nltk
from tools.nlp import tokenize

from requests import get as requests_get
import conf.conf as conf
import json

nltk.download('punkt_tab', quiet=True)

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = conf.SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

app.tokens_index = {}
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
    while len(json.loads(response.text)[0]) > 250:
        response = requests_get(
            url="https://api.api-ninjas.com/v1/quotes?category=education",
            headers={"X-Api-Key": conf.API_KEY_QUOTES},
        )

    quote = dict()

    if response.status_code != 200:
        quote["quote"] = "error loading a quote. :( #yxzhinCodeMoment"
        quote["author"] = ""

    else:
        quote = json.loads(response.text)[0]

    # //04.12.2024.

    query = quote["author"]

    if query != "":
        response = requests_get(
            url=f"https://www.googleapis.com/customsearch/v1?q={query}\
                &searchType=image&key={conf.API_KEY_IMAGES}\
                &cx={conf.API_CX_IMAGES}",
        )

        # print(response.status_code, response.text)

        if response.status_code != 200:
            image_url = ""

        else:
            image_url = json.loads(response.text)["items"][0]["link"]

    quote["image_url"] = image_url

    # print("[debug] image_url: ", image_url)

    g.quote = quote

    # //end of my part

    g.search_form = SearchForm()
    if g.search_form.validate_on_submit():
        return redirect(f"/search/{g.search_form.search.data}")


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


@app.route('/search/<string:search_text>', methods=["GET", "POST"])
def search(search_text: str):
    ids = []
    search_token = tokenize(search_text)

    for book_id, token in app.tokens_index.items():
        num_matching_words = len(search_token & token)
        if num_matching_words > 0:
            ids.append((book_id, num_matching_words))

    ids.sort(key=lambda x: x[1], reverse=True)
    ids = [i[0] for i in ids]

    sess = db_session.create_session()
    search_results = sess.query(Book).filter(Book.id.in_(ids)).all()
    return render_template("search.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           search_results=search_results,
                           search_text=search_text,
                           title="Search results",
                           search_form=g.search_form)


@app.route('/library', methods=["GET", "POST"])
def library():
    return redirect('/')


@app.route('/library/<string:book_id>', methods=["GET", "POST"])
def library_book(book_id: str):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book is None:
        return render_template("book.html",
                               quote=g.quote["quote"],
                               author=g.quote["author"],
                               answer="",
                               title="Pregled knjige",
                               search_form=g.search_form)
    book_dict = book.to_dict()
    return render_template("book.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           answer=True,
                           title="Pregled knjige",
                           book=book_dict,
                           search_form=g.search_form)


@app.route('/uploads/books/<filename>')
def serve_pdf(filename):
    return send_from_directory('uploads/books', filename)


@app.route('/add', methods=["GET", "POST"])
def add():
    add_form = AddBookForm()
    if not current_user.is_authenticated:
        return render_template("add_book.html",
                               quote=g.quote["quote"],
                               author=g.quote["author"],
                               title="Dodavanje knjige",
                               search_form=g.search_form,
                               book_form=add_form,
                               answer="Samo autentifikovani korisnici mogu da dodaju knjige")
    if add_form.validate_on_submit():
        file = add_form.file.data
        filename = f"{add_form.title.data} – {add_form.author_name.data} ({add_form.year.data}).pdf"
        filepath = f"uploads/books/{filename}"
        book_dict = {
            "title": add_form.title.data,
            "uploaded_user_id": 1,
            "author_name": add_form.author_name.data,
            "path": filepath,
            "description": add_form.description.data,
            "year": add_form.year.data,
            "grade": add_form.grade.data
        }
        book_id = addBook(book_dict)
        file.save(filepath)
        flash(f"Knjiga je uspešno dodata na lokaciju {filepath}")

        # books and authors tokens for search
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == book_id).first()
        app.tokens_index[book.id] = tokenize(book.title) | tokenize(book.author.name)
        return redirect("/add")
    return render_template("add_book.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           title="Dodavanje knjige",
                           search_form=g.search_form,
                           book_form=add_form,
                           answer="")


@app.route('/edit/<int:book_id>', methods=["GET", "POST"])
def edit(book_id: int):
    edit_form = EditBookForm()
    if not current_user.is_authenticated:
        return render_template("add_book.html",
                               quote=g.quote["quote"],
                               author=g.quote["author"],
                               title="Editovanje knjige",
                               search_form=g.search_form,
                               book_form=edit_form,
                               answer="Samo autentifikovani korisnici mogu da edituju knjige!")

    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book is None:
        return render_template("add_book.html",
                               quote=g.quote["quote"],
                               author=g.quote["author"],
                               title="Editovanje knjige",
                               search_form=g.search_form,
                               book_form=edit_form,
                               answer="Knjiga sa datim id ne postoji!")

    if request.method == "GET":
        edit_form.title.data = book.title
        edit_form.author_name.data = book.author.name
        edit_form.description.data = book.description
        edit_form.year.data = book.year
        edit_form.grade.data = book.grade

    if edit_form.validate_on_submit():
        author = db_sess.query(Author).filter(Author.name == edit_form.author_name.data).first()

        book.title = edit_form.title.data
        book.author_id = author.id
        book.description = edit_form.description.data
        book.year = edit_form.year.data
        book.grade = edit_form.grade.data
        book.author = author

        db_sess.commit()

        app.tokens_index = {}
        books = db_sess.query(Book).all()
        for b in books:
            app.tokens_index[b.id] = tokenize(b.title) | tokenize(b.author.name)
        return redirect(f"/library/{book.id}")

    return render_template("add_book.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           title="Editovanje knjige",
                           search_form=g.search_form,
                           book_form=edit_form,
                           answer="")


@app.route('/')
def index():
    return render_template("index.html",
                           quote=g.quote["quote"],
                           author=g.quote["author"],
                           title="Online biblioteka",
                           search_form=g.search_form,
                           books=app.main_page_books)


def addBook(book: dict) -> int:
    db_sess = db_session.create_session()
    author = db_sess.query(Author).filter(
        Author.name == book["author_name"]).first()
    if author is None:
        author = Author(name=book["author_name"])
        db_sess.add(author)

    book = Book(
        title=book["title"],
        uploaded_user_id=1,
        author_id=db_sess.query(Author).filter(Author.name == book["author_name"]).first().id,
        path=book["path"],
        description=book["description"],
        year=book["year"],
        grade=book["grade"],
    )
    db_sess.add(book)
    db_sess.commit()
    return book.id


def main() -> None:
    db_session.global_init("db/library.sqlite")
    db_sess = db_session.create_session()

    # books and authors tokens for search
    books = db_sess.query(Book).all()
    for b in books:
        app.tokens_index[b.id] = tokenize(b.title) | tokenize(b.author.name)

    # getting dicts of 5 books of every grade from 1 to 4
    app.main_page_books = [
        [book.to_dict() for book in db_sess.query(Book).filter(Book.grade == i).limit(3).all()] for i in range(1, 5)
    ]
    app.run(host=HOST, port=PORT, debug=True, threaded=True)


if __name__ == "__main__":
    main()
