function toggleSearchResults() {
    let results = document.getElementById('search-results');
    let currentState = results.style.display;

    if (currentState == "") {
        results.style.display = 'none';
    } else {
        results.style.display = '';
    }
}

function updateSearchResults() {
    let searchQuerry = document.getElementById('search-input').value;
    console.log(searchQuerry);

    // TODO
}

function checkSubmit(e) {
    if(e && e.keyCode == 13) {
       document.forms[0].submit();
    }
 }