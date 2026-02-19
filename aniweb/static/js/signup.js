const form = document.getElementById("signup-form");
const email_id = document.getElementById("email");
const email_span = document.getElementById("email_span");
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const password_id = document.getElementById("password");
const password_span = document.getElementById("password_span");
const submit_button = document.getElementById("submit_button");


async function signUpToAccount( email, password) {
    const response = await fetch("/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({email: email, password: password})
    });
    return response;
}


email_id.addEventListener("input", async () => {
    const isValid = !emailRegex.test(email_id.value)
    email_id.style.borderColor = isValid ? "red" : "#c9242490";
    email_span.style.color = isValid ? "red" : "transparent";
});

email_id.addEventListener("focus", async () => {
    const isValid = !emailRegex.test(email_id.value)
    email_id.style.borderColor = isValid ? "red" : "#c9242490";
    email_span.style.color = isValid ? "red" : "transparent";
});

email_id.addEventListener("blur", async () => {
    const isValid = email_id.value.trim().length > 0 && !emailRegex.test(email_id.value);
    email_id.style.borderColor = isValid ? "red" : "#c9242460";
    email_span.style.color = isValid ? "red" : "transparent";
});



password_id.addEventListener("input", async () => {
    const isValid = password_id.value.trim().length >= 0 && password_id.value.trim().length < 8;
    password_id.style.borderColor = isValid ? "red" : "#c9242490";
    password_span.style.color = isValid ? "red" : "transparent";

    if (/\s/.test(password_id.value)) {
        password_id.value = password_id.value.replace(/\s/g, "");
    }
});

password_id.addEventListener("focus", async () => {
    const isValid = password_id.value.trim().length >= 0 && password_id.value.trim().length < 8;
    password_id.style.borderColor = isValid ? "red" : "#c9242490";
    password_span.style.color = isValid ? "red" : "transparent";
});

password_id.addEventListener("blur", async () => {
    const isValid = password_id.value.trim().length > 0 && password_id.value.trim().length < 8;
    password_id.style.borderColor = isValid ? "red" : "#c9242460";
    password_span.style.color = isValid ? "red" : "transparent";
});



form.addEventListener("input", async () => {
    const isValid = emailRegex.test(email_id.value) && password_id.value.trim().length >= 8;
    submit_button.disabled = isValid ? false : true;
});

submit_button.addEventListener("click", async (e) => {
    e.preventDefault();

    if (emailRegex.test(email_id.value) && password_id.value.trim().length >= 8) {
        const response = await signUpToAccount(email_id.value, password_id.value.trim());
        if (response.status === 401) {
            console.log("Unathorized");
        } else if (response.status === 200) {
            window.location.href = "/";
        } else {
            console.log(response.status);
        }
    }
});