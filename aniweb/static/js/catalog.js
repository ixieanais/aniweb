const toggleGenresButton = document.getElementById("toggle-genres");
const hiddenGenres = document.querySelectorAll(".hidden-genre");

let expanded = false;

toggleGenresButton.addEventListener("click", () => {
    expanded = !expanded;

    hiddenGenres.forEach(el => {
        el.style.display = expanded ? "block" : "none";
    });

    toggleGenresButton.textContent = expanded ? "свернуть" : "все жанры";
});

function goToPage(page) {
    const url = new URL(window.location.href);
    url.searchParams.set("page", page);
    window.location.href = url.toString();
}

document.getElementById("applyFilters").addEventListener("click", () => {
    const url = new URL(window.location.href);

    let sortValue = document.getElementById("sort").value;
    let statusValue = document.getElementById("status").value;

    if (sortValue === "choose") {
        url.searchParams.delete("sort");
    } else {
        url.searchParams.set("sort", sortValue);
    }

    if (statusValue === "choose") {
        url.searchParams.delete("status");
    } else {
        url.searchParams.set("status", statusValue);
    }

    const checkedGenres = Array.from(
        document.querySelectorAll('input[name="genres"]:checked')
    ).map(el => el.value);

    if (checkedGenres.length === 0) {
        url.searchParams.delete("genres");
    } else {
        url.searchParams.set("genres", checkedGenres.join(","));
    }

    url.searchParams.delete("page");

    window.location.href = url.toString();
});

if (document.getElementById("not-found")) {
    document.getElementById("not-found-button").addEventListener("click", async () => {
        const url = new URL(window.location.href);

        url.searchParams.delete("page");
        url.searchParams.delete("genres");
        url.searchParams.delete("sort");
        url.searchParams.delete("status");

        window.location.href = url.toString();
    });
}