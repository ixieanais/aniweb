async function deleteViewTime(episode_id) {
    const response = await fetch(`/view_time/${episode_id}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });
    console.info(await response.json());
}

document.querySelectorAll(".delete-queue-button").forEach(button => {
    const episodeId = button.dataset.id;

    button.addEventListener("click", async (e) => {
        e.stopPropagation();
        e.preventDefault();

        await deleteViewTime(episodeId);

        window.location.href = window.location.href;
    });
});