const searchWrapper = document.querySelector(".search-wrapper");
const searchInput = searchWrapper.querySelector("input");
let searchTimer;


searchInput.addEventListener("input", async () => {
    const value = searchInput.value.trim();

    clearTimeout(searchTimer);

    if (value.length > 2) {
        searchTimer = setTimeout(async () => {
            addDiv(value);
        }, 500);
    }

    var searchResultsDiv = document.querySelector(".search-result");
    if (searchResultsDiv) {
        searchResultsDiv.remove();
    }
});


async function addDiv(query) {
    if (document.querySelector(".search-result")) return;

    const releases = await searchReleases(query);
    if (releases.data.length === 0) return;

    const div = document.createElement("div");
    div.className = "search-result";
    div.style.width = `${searchInput.offsetWidth}px`;

    releases.data.forEach(element => {
        var linkItem = document.createElement("a");
        linkItem.href = `/release/${element.alias}`;
        linkItem.innerHTML = `
            <div class="search-item">
                <img src="https://anilibria.tv/${element.poster.optimized.preview}">
                <span>${element.name.main}</span>
            </div>
        `;
        div.appendChild(linkItem);
    });

    searchWrapper.appendChild(div);
}

document.addEventListener("click", async (e) => {
    var searchResultsDiv = document.querySelector(".search-result");

    if (searchResultsDiv) {
        if (!searchResultsDiv.contains(e.target) && e.target != searchInput) {
            searchResultsDiv.remove();
        }
    }
});

async function searchReleases(query) {
    const response = await fetch(`/search?query=${query}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}