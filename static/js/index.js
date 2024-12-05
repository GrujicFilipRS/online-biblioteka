let text = document.getElementById('books').getAttribute('data');

text = text.replace('to " biografske duse ".', 'to biografske duse.');
text = text.replace('Viljema Šekspira, \'Hamlet\' je priča', 'Viljema Šekspira, Hamlet je priča');
text = text.replace('sumnju. \'Hamlet\' važi', 'sumnju. Hamlet važi');
text = text.replace('od \'najprestižnijih\' Šekspirovih', 'od najprestižnijih Šekspirovih');
console.log(text);
console.log(text.length);

//console.log(document.getElementById('books').getAttribute('data').replaceAll('\'', '"').replaceAll('None', 'null'));
var books = pythonDictToJsObject(text);

console.log(books)

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

function putBookIntoPreview(cl, id) {
    let razred = document.getElementsByClassName(`r${cl+1}`)[0];
    console.log(`r${cl+1}`);
    let lektira = razred.getElementsByClassName(`lek${id+1}`)[0];
    let title = lektira.getElementsByClassName('lek-title')[0];
    let author = lektira.getElementsByClassName('lek-author')[0];
    let desc = lektira.getElementsByClassName('lek-desc')[0];
    let image = lektira.getElementsByClassName('lek-right-div')[0].children[0];

    try{
        title.textContent = Book.books[cl*3+id].name;
    } catch(error) {
        console.log('blya1');
    }

    try{
        author.textContent = Book.books[cl*3+id].getAuthor().name;
    } catch(error) {
        throw(error);
    }

    try{
        desc.textContent = Book.books[cl*3+id].desc.substring(0, 110) + '...';
    } catch(error) {
        console.log('blya3');
    }

    try {
        image.setAttribute('src', `${Book.books[cl*3+id].getAuthor().image}`);
    } catch(error) {
        console.log('blya4');
    }
    
}

for(let i = 0; i < 4; i++) {
    for(let j = 0; j < 5; j++) {
        console.log(books[i][j]);
        Book.parseJSON(books[i][j]);
        if (j < 3)
            putBookIntoPreview(i, j);
    }
}

booksFirstGrade = [Book.books[0], Book.books[1], Book.books[2], Book.books[3], Book.books[4]]
booksSecondGrade = [Book.books[5], Book.books[6], Book.books[7], Book.books[8], Book.books[9]]
booksThirdGrade = [Book.books[10], Book.books[11], Book.books[12], Book.books[13], Book.books[14]]
booksFourthGrade = [Book.books[15], Book.books[16], Book.books[17], Book.books[18], Book.books[19]]

scrolled = {0: 0, 1: 0, 2: 0, 3: 0}

function goLeftFirst() {
    scrolled[0] -= 1;
    updateList();
}

function goRightFirst() {
    scrolled[0] += 1;
    updateList();
}

function goLeftSecond() {
    scrolled[1] -= 1;
    updateList();
}

function goRightSecond() {
    scrolled[1] += 1;
    updateList();

}

function goLeftThird() {
    scrolled[2] -= 1;
    updateList();
}

function goRightThird() {
    scrolled[2] += 1;
    updateList();
}

function goLeftFourth() {
    scrolled[3] -= 1;
    updateList();
}

function goRightFourth() {
    scrolled[3] += 1;
    updateList();
}

function updateList() {
    for(let cl = 0; cl < 4; cl++) {
        for(let id = 0; id < 3; id++) {
            let razred = document.getElementsByClassName(`r${cl+1}`)[0];
            console.log(`r${cl+1}`);
            let lektira = razred.getElementsByClassName(`lek${id+1}`)[0];
            let title = lektira.getElementsByClassName('lek-title')[0];
            let author = lektira.getElementsByClassName('lek-author')[0];
            let desc = lektira.getElementsByClassName('lek-desc')[0];
            let image = lektira.getElementsByClassName('lek-right-div')[0].children[0];

            let win = [];
            for(let i = 0; i < 3; i++) {
                win.push((scrolled[cl] + i) % 4);
            }
            console.log(win);
        }
    }
}