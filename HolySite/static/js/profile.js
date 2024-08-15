var botButton = document.getElementById("botButton");
var botText = document.getElementById("botText")

function Toast(success, text) {
    Toastify({
        text: text,
        duration: 3000,
        newWindow: true,
        close: false,
        gravity: "bottom",
        position: "right",
        stopOnFocus: false,
        style: {
            background: (success ? "#22c55e" : "#dc2626"),
        },
    }).showToast();
}

let CONNECTING = false;

async function toggleBot() {
    if (CONNECTING) {
        return;
    }
    CONNECTING = true
    botButton.style.cursor = "wait";
    let response = await fetch("/profile", { method: "POST", credentials: "same-origin" })

    if (response.status === 429) {
        Toast(false, "Слишком много запросов, повторите попытку позже.");
    } else if (response.status == 500) {
        Toast(false, "Что-то сломалось, повторите попытку позже.")
    } else if (response.status == 200) {
        json = await response.json()
        if (json["success"] && json["status"] == "connected") {
            botButton.innerText = "Отключить"
            botText.innerText = "Бот подключен на вашем канале"
            Toast(true, "Бот был успешно подключен!")
        } else if (json["success"] && json["status"] == "disconnected") {
            botButton.innerText = "Подключить"
            botText.innerText = "Бот отключен на вашем канале"
            Toast(true, "Бот был успешно отключен!")
        } else {
            Toast(true, json["error"])
        }
    }
    botButton.style.cursor = "pointer";
    CONNECTING = false
}
