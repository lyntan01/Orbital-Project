function showAlert(message) {
    alert(message);
}

function submitForm(formName) {
    document.forms[formName].submit();
    alert("Form submitted!") // debugging
}