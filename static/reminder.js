function startReminder(minutes) {
    localStorage.setItem("reminderEnabled", "true");
    localStorage.setItem("reminderInterval", minutes);

    alert(`Reminder set! We'll remind you every ${minutes} minute(s).`);
}

function stopReminder() {
    localStorage.removeItem("reminderEnabled");
    localStorage.removeItem("reminderInterval");
}

function checkReminder() {
    const enabled = localStorage.getItem("reminderEnabled");
    const interval = parseInt(localStorage.getItem("reminderInterval"));

    if (enabled && interval > 0) {
        setInterval(() => {
            alert("⏰ Reminder: It's time to change your password!");
        }, interval * 60000); // convert minutes to ms
    }
}

document.addEventListener("DOMContentLoaded", checkReminder);