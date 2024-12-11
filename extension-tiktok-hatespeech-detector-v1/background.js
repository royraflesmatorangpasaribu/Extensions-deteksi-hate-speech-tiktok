function injectContentScript(tabId) {
    chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ["content.js"]
    });
    console.log("Content script injected into tab:", tabId);
}

// Menghapus content script dengan me-reload halaman TikTok saat toggle dimatikan
function removeContentScript(tabId) {
    chrome.tabs.reload(tabId); // Reload halaman untuk menghapus script
    console.log("Content script removed from tab:", tabId);
}

// Monitor perubahan toggle
chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.toggleState) {
        if (changes.toggleState.newValue) {
            console.log("Toggle is ON, starting URL monitoring");
            startMonitoringTikTok(); // Mulai memonitor jika toggle diaktifkan
        } else {
            console.log("Toggle is OFF, stopping URL monitoring");
            stopMonitoringTikTok(); // Hentikan monitoring jika toggle dimatikan
        }
    }
});

// Memulai monitoring TikTok URL dengan inject content script
function startMonitoringTikTok() {
    chrome.tabs.query({ url: "*://*.tiktok.com/*" }, (tabs) => {
        tabs.forEach((tab) => {
            if (tab.status === "complete") {
                injectContentScript(tab.id);
            }
        });
    });
}

// Menghentikan monitoring TikTok URL dengan me-reload halaman
function stopMonitoringTikTok() {
    chrome.tabs.query({ url: "*://*.tiktok.com/*" }, (tabs) => {
        tabs.forEach((tab) => removeContentScript(tab.id));
    });
}

// Menangkap event tab di-refresh atau navigasi ke TikTok baru
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete" && tab.url.includes("tiktok.com")) {
        chrome.storage.local.get("toggleState", (data) => {
            if (data.toggleState) {
                injectContentScript(tabId);
                console.log("Tab updated or refreshed, content script injected for URL:", tab.url);
            }
        });
    }
});

// Mengecek status awal toggle untuk memulai monitoring jika diperlukan
chrome.storage.local.get("toggleState", (data) => {
    if (data.toggleState) {
        startMonitoringTikTok();
    }
});