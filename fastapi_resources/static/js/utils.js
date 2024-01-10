const shutdown_button = document.querySelector("div.shutdown")
const shutdown_overlay = document.querySelector("div.shutdown_overlay")

// Sends a request to the server for a shutdown. If the server is successfully shutdown, an overlay pops up notifying
// the user that the server has been shutdown.
shutdown_button.addEventListener("click", () => {
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"message":"message"}),
        headers: {"Content-type": "application/json"}
    }
    fetch("/shutdown", fetch_body)

    shutdown_overlay.style["display"] = "flex";
})