class Book {
    static books = [];
    constructor(id, uploadDate, uploadedUserID, name, authorID, desc) {
        this.id = id;
        this.uploadDate = uploadDate;
        this.uploadedUserID = uploadedUserID;
        this.name = name;
        this.authorID = authorID;
        this.desc = desc;

        Book.books.push(this);
    }

    static parseJSON(json) {
        let id = json['id'];
        let uploadDate = json['uploadDate'];
        let uploadedUserID = json['uploadedUserID'];
        let name = json['name'];
        let authorID = json['authorID'];
        let desc = json['desc'];

        let book = new Book(id, uploadDate, uploadedUserID, name, authorID, desc);
        return book;
    }

    getAuthor() {
        Author.authors.forEach(author => {
            if (author.id == this.authorID)
                return author;
        });
    }
};