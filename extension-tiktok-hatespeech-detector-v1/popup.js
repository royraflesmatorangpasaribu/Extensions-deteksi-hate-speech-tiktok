document.getElementById("toggleSwitch").addEventListener("change", function () {
    const isOn = this.checked;
    const message = isOn ? "Toggle is ON" : "Toggle is OFF";
    
    document.getElementById("status").innerText = message;
    chrome.storage.local.set({ toggleState: isOn }); // Store state in Chrome storage
  
    // Optional: Send message to background script if needed
    chrome.runtime.sendMessage({ toggleState: isOn });
});
  
// Load the saved state when the popup is opened
chrome.storage.local.get("toggleState", (data) => {
    const toggleSwitch = document.getElementById("toggleSwitch");
    toggleSwitch.checked = data.toggleState || false;
    document.getElementById("status").innerText = toggleSwitch.checked ? "Toggle is ON" : "Toggle is OFF";
});

document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("toggleSwitch");
    const statusText = document.getElementById("status");
    const loadingElement = document.getElementById("loading");
  
    // Muat status toggle dan loading dari storage saat plugin dibuka
    chrome.storage.local.get(["toggleState", "isLoading"], (data) => {
        const isOn = data.toggleState || false;
        toggleSwitch.checked = isOn;
        statusText.textContent = isOn ? "Extension Aktif" : "Extension Tidak Aktif";
        statusText.classList.toggle("on", isOn);
        statusText.classList.toggle("off", !isOn);
  
        loadingElement.style.display = data.isLoading ? "block" : "none";
    });
  
    // Event listener untuk perubahan toggle
    toggleSwitch.addEventListener("change", function () {
        const isOn = toggleSwitch.checked;
        statusText.textContent = isOn ? "Extension Aktif" : "Extension Tidak Aktif";
        statusText.classList.toggle("on", isOn);
        statusText.classList.toggle("off", !isOn);
  
        chrome.storage.local.set({ toggleState: isOn });
    });
  
    // Mendengarkan pesan dari background script untuk update status loading
    chrome.runtime.onMessage.addListener((message) => {
        if (message.type === "loadingStatus") {
            loadingElement.style.display = message.isLoading ? "block" : "none";
            chrome.storage.local.set({ isLoading: message.isLoading });
        }
    });
});