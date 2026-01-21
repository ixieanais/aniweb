async function updateViewedState(episode_id, release_id) {
    const response = await fetch("/viewed", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({episode_id: episode_id, release_id: release_id})
    });
    console.info(await response.json());
}

async function saveViewTime(episode_id, time) {
    const response = await fetch(`/view_time/${episode_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({time: time})
    });
    console.info(await response.json());
}

async function updateViewTime(episode_id, time) {
    const response = await fetch(`/view_time/${episode_id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({time: time})
    });
    console.info(await response.json());
}

async function deleteViewTime(episode_id) {
    const response = await fetch(`/view_time/${episode_id}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });
    console.info(await response.json());
}

document.getElementById("video-preview").addEventListener("click", async () => {
    const videoPreview = document.getElementById("video-preview");
    const video = document.getElementById("player");
    const episodeId = video.dataset.id;

    const openingData = JSON.parse(video.dataset.opening);
    let startOpening = openingData["start"];
    let endOpening = openingData["end"];

    const endingData = JSON.parse(video.dataset.ending);
    let startEnding = endingData["start"];
    const endEnding = endingData["end"];

    let viewed = JSON.parse(video.dataset.isViewed);

    videoPreview.style.display = "none";
    video.style.display = "block";

    const player = new Plyr(video, {
        settings: ['quality', 'speed'],
        quality: {
        default: 720,
        options: [1080, 720, 480],
        forced: true,
        onChange: updateQuality
        },
        keyboard: { focused: false, global: true },
        disableContextMenu: false,
    });

    var hls;

    function loadHls(url) {
        if (hls) {
            hls.destroy();
        }

        if (Hls.isSupported()) {
            hls = new Hls();
            hls.loadSource(url);
            hls.attachMedia(video);
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
            video.src = url;
        }
    }

    function updateQuality(newQuality) {
        const currentTime = video.currentTime;
        const isPaused = video.paused;

        loadHls(sources[newQuality]);

        video.onloadedmetadata = () => {
            video.currentTime = currentTime;
            if (!isPaused) video.play();
        }
    }

    loadHls(sources[720]);

    const skipButtonContainer = document.createElement("div");
    skipButtonContainer.classList.add("plyr__custom-left-button");

    const skipButton = document.createElement("button");
    skipButton.textContent = "Пропустить";
    skipButtonContainer.appendChild(skipButton);

    const nextEpisodeContainer = document.createElement("div");
    nextEpisodeContainer.classList.add("plyr__custom-right-button");

    const nextEpidoseA = document.createElement("a");
    nextEpidoseA.href = `/video/${video.dataset.nextEpisodeId}`;
    nextEpisodeContainer.appendChild(nextEpidoseA);

    const nextEpisodeButton = document.createElement("button");
    nextEpisodeButton.textContent = "Следующий эпизод";
    nextEpidoseA.appendChild(nextEpisodeButton);

    player.elements.container.appendChild(skipButtonContainer);
    player.elements.container.appendChild(nextEpisodeContainer);

    let currentTime;
    let viewTimeSaved = false;
    let viewTimeDeleted = false;
    if (viewed) {
        viewTimeDeleted = true;
        await deleteViewTime(episodeId);
    }

    video.addEventListener("loadedmetadata", async () => {
        if (startEnding === null) startEnding = video.duration - 120;

        if (video.dataset.viewTime > 0) {
            video.currentTime = video.dataset.viewTime;
        }

        video.addEventListener("timeupdate", async () => {
            if (video.currentTime >= startOpening && video.currentTime <= endOpening && startOpening != null && endOpening != null) {
                skipButton.style.display = "block";
            } else {
                skipButton.style.display = "none";
            }

            if (video.currentTime >= startEnding && video.currentTime <= endEnding && video.dataset.nextEpisodeId != "") {
                nextEpisodeButton.style.display = "block";
            } else {
                nextEpisodeButton.style.display = "none";
            }

            if (video.currentTime >= startEnding - 20 && !viewed) {
                await updateViewedState(episodeId, video.dataset.releaseId);
                viewed = true;
            }

            if (Math.floor(video.currentTime) % 10 == 0 && currentTime != Math.floor(video.currentTime)) {
                if (!viewed) {
                    currentTime = Math.floor(video.currentTime);
                    if (!viewTimeSaved) {
                        await saveViewTime(episodeId, currentTime);
                        viewTimeSaved = true;
                    } else {
                        await updateViewTime(episodeId, currentTime);
                    }
                } else {
                    if (!viewTimeDeleted) {
                        await deleteViewTime(episodeId);
                        viewTimeDeleted = true;
                        if (video.dataset.nextEpisodeId != "") {
                            await saveViewTime(video.dataset.nextEpisodeId, 0);
                        }
                    }
                }
            }
        });
    });

    skipButton.addEventListener("click", () => {
        player.currentTime = endOpening + 1;
        skipButton.style.display = "none";
    });
});