class Author {
    static authors = [];
    constructor(id, name, desc) {
        this.id = id;
        this.name = name;
        this.desc = desc;
        
        Author.authors.push(this);
    }

    static parseJSON(json) {
        let id = json['id'];
        let name = json['name'];
        let desc = json['desc'];

        let author = new Author(id, name, desc);
        return author;
    }

    getBooks() {
        let books = [];

        Book.books.forEach(book => {
            if (this.id == book.authorID)
                books.push(book);
        });
        
        return books;
    }
};