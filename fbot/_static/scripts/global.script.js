$(document).ready(() => {
    setInterval(() => {
        $.post("/keep-alive", {}).fail((e) => {
            alert("Server down, restart server.");
            console.error(e);
        });
    }, 8000);
});