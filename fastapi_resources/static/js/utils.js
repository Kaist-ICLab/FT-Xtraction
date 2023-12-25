const shutdown_button = document.querySelector("div.shutdown")
const shutdown_overlay = document.querySelector("div.shutdown_overlay")

shutdown_button.addEventListener("click", () => {
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"message":"message"}),
        headers: {"Content-type": "application/json"}
    }
    fetch("/shutdown", fetch_body)

    shutdown_overlay.style["display"] = "flex";
})