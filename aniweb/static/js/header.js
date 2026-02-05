const searchWrapper = document.querySelector(".search-wrapper");
const searchInput = searchWrapper.querySelector("input");
const profileButton = document.getElementById("profile");
let searchTimer;
let favoritesCount;
let viewedCount;


async function searchReleases(query) {
    const response = await fetch(`/search?query=${query}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
} 

async function getFavoritesCount() {
    const response = await fetch("/favorites_count", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function getViewedCount() {
    const response = await fetch("/viewed_count", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}


async function addDiv(query) {
    if (document.querySelector(".search-result")) return;

    const releases = await searchReleases(query);
    if (releases.data.length === 0) return;

    const div = document.createElement("div");
    div.className = "search-result";
    width = searchInput.offsetWidth;
    if (width < 150) {
        width = 250;
    }
    div.style.width = `${width}px`;

    releases.data.forEach(element => {
        var linkItem = document.createElement("a");
        linkItem.href = `/release/${element.alias}`;
        linkItem.innerHTML = `
            <div class="search-item">
                <img src="https://anilibria.tv/${element.poster.optimized.preview}">
                <span title="${element.name.main}">${element.name.main}</span>
            </div>
        `;
        div.appendChild(linkItem);
    });

    searchWrapper.appendChild(div);
}

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


function plural(n, one, two, five) {
    n = Math.abs(n);

    if (n % 100 >= 11 && n % 100 <= 14) return five;

    const last = n % 10;

    if (last === 1) return one;
    if (last >= 2 && last <= 4) return two;
    return five;
}

async function createProfileContainer() {
    const profileDiv = document.createElement("div");
    profileDiv.className = "profile-wrapper";
    profileButton.parentElement.appendChild(profileDiv);

    if (favoritesCount === undefined || viewedCount === undefined) {
        profileDiv.innerHTML = `
        <div class="loader"></div>
        `;

        var favoritesCountDiv = await getFavoritesCount();
        var viewedCountDiv = await getViewedCount();
        favoritesCount = favoritesCountDiv;
        viewedCount = viewedCountDiv;
    } else {
        var favoritesCountDiv = favoritesCount;
        var viewedCountDiv = viewedCount;
    }

    profileDiv.innerHTML = `
    <div class="line"></div>
    <div class="profile-item">
        <span class="text-halfgray">В избранном</span>
        <span class="text-lightgray">${favoritesCountDiv} ${plural(favoritesCountDiv, "релиз", "релиза", "релизов")}</span>
    </div>
    <div class="line"></div>
    <div class="profile-item">
        <span class="text-halfgray">Просмотрено</span>
        <span class="text-lightgray">${viewedCountDiv} ${plural(viewedCountDiv, "эпизод", "эпизода", "эпизодов")}</span>
    </div>
    <div class="line"></div>
    `;
}

profileButton.addEventListener("click", async () => {
    const profileContainer = document.querySelector(".profile-wrapper");
    if (profileContainer) {
        profileContainer.remove();
        return;
    }

    await createProfileContainer();
});


document.addEventListener("click", async (e) => {
    const profileContainer = document.querySelector(".profile-wrapper");
    if (profileContainer) {
        if (!profileContainer.contains(e.target) && !profileButton.contains(e.target)) {
            profileContainer.remove();
        }
    }

    const searchResultsDiv = document.querySelector(".search-result");
    if (searchResultsDiv) {
        if (!searchResultsDiv.contains(e.target) && e.target != searchInput) {
            searchResultsDiv.remove();
        }
    }
});

// function test() {
//     const profileDiv = document.createElement("div");
//     profileDiv.className = "profile-wrapper";
//     profileDiv.innerHTML = `
//     <div class="loader"></div>
//     `;
//     profileButton.parentElement.appendChild(profileDiv);
// }

// test()