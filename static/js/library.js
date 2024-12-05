function pythonDictToJsObject(pythonDictString) {
    try {
        // Zameni jednostruke navodnike dvostrukim i "None" sa "null"
        let jsonString = pythonDictString
            .replace('e.\'', 'e."')
            .replace(/'/g, '"') // Zamena jednostrukih navodnika
            .replace(/None/g, 'null') // Zamena Python None sa null
            .replace(/True/g, 'true') // Zamena Python True sa true
            .replace(/False/g, 'false'); // Zamena Python False sa false

        // Pretvori string u JavaScript objekat
        let jsObject = JSON.parse(jsonString);

        return jsObject;
    } catch (error) {
        console.error("Greška pri konverziji:", error.message);
        return null;
    }
}

let text = document.getElementById('book').getAttribute('data');

console.log(text);

let book = Book.parseJSON(pythonDictToJsObject(text));

console.log(book);

let preview = document.getElementById('preview');

preview.setAttribute('src', `../../uploads/books/${book.path}`);