function showComment(){
    var x = document.getElementById("comment-area");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function showField(){
    var x = document.getElementById("comment-area");
    if (x.style.display === "none") {
        x.style.display = "block";
    } 
}

function hideField(){
    var x = document.getElementById("comment-area");
    if (x.style.display === "block") {
        x.style.display = "none";
    }
}