function disable_funct() {
    var elements = document.getElementsByClassName("btn");
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].type == "submit") {
            elements[i].disabled = true;
            elements[i].innerHTML = 'Sending…';
        }
    }
}


function dom_funct() {
    var elements = document.getElementsByTagName("form")
    for (var i = 0; i < elements.length; i++) {
        elements[i].addEventListener('submit', disable_funct, false);
    }
}

document.addEventListener("DOMContentLoaded", dom_funct);
