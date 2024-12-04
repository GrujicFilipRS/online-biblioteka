class Book {
    static books = [];
    constructor(id, uploadDate, uploadedUserID, name, authorID, desc, grade, path) {
        this.id = id;
        this.uploadDate = uploadDate;
        this.uploadedUserID = uploadedUserID;
        this.name = name;
        this.authorID = authorID;
        this.desc = desc;
        this.grade = grade
        this.path = path

        Book.books.push(this);
    }

    static parseJSON(json) {
        let id = json['id'];
        let uploadDate = json['year'];
        let uploadedUserID = json['uploaded_user_id'];
        let name = json['title'];
        let authorID = json['author']['id'];
        let desc = json['description'];
        let grade = json['grade'];
        let path = json['path'];

        let book = new Book(id, uploadDate, uploadedUserID, name, authorID, desc, grade, path);
        
        if (book.getAuthor() == undefined) {
            console.log('pokusao sam dodati');
            Author.parseJSON(json['author']);
        }

        return book;
    }

    getAuthor() {
        for (let author of Author.authors) {
            if (author.id === this.authorID) {
                return author; // Ovdje se vraća autor odmah čim se nađe
            }
        }
        return undefined; // Ako nije pronađen autor, vratiti undefined
    }
};

