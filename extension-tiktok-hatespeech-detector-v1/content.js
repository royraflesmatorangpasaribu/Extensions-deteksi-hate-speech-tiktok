let lastUrl = location.href;
console.log("Initial URL:", lastUrl);

// Selector fleksibel untuk elemen komentar dan container
const commentsSelector = '[class*="PCommentText"] span, [class*="CommentText"] span';
const containerSelector = '[class*="DivCommentListContainer"]';

// Extract dan log content ID saat halaman pertama kali dimuat
const initialContentId = extractContentId(lastUrl);
if (initialContentId) {
    console.log("Initial content_id:", initialContentId);
    var controller = new AbortController(); // Inisialisasi controller
    var signal = controller.signal;

    startScraping(initialContentId);
} else {
    console.log("No content ID found in the initial URL");
}

// Mengekstrak content ID dari URL
function extractContentId(url) {
    const match = url.match(/\/video\/(\d+)/);
    return match ? match[1] : null;
}

// Memeriksa perubahan URL secara periodik
function checkUrlChange() {
    const currentUrl = location.href;
    if (currentUrl !== lastUrl) {
        console.log("URL has changed. Old URL:", lastUrl, "New URL:", currentUrl);
        abortFetching();

        lastUrl = currentUrl;
        controller = new AbortController(); // Reset controller
        signal = controller.signal;

        const contentId = extractContentId(currentUrl);
        if (contentId) {
            console.log("New content_id:", contentId);
            startScraping(contentId);
        } else {
            console.log("No content ID found in the new URL");
        }
    }
}

// Menghentikan proses fetch API
function abortFetching() {
    console.log('Aborting current fetch request');
    controller.abort();
}

// Memulai proses scraping data dari API
function startScraping(contentId) {
    console.log('Starting scraping with content_id:', contentId);

    fetch("http://127.0.0.1:8000/scrape-comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_comment: contentId }),
        signal: signal
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('Data received from API:', data);
        hateSpeechComments = data.comments;
        detectHateSpeech(hateSpeechComments);
        observeNewComments();
    })
    .catch(error => {
        if (error.name === 'AbortError') {
            console.log('Fetching aborted');
        } else {
            console.error("Error during API fetch:", error);
        }
    })
}

// Memantau komentar baru dengan MutationObserver
function observeNewComments() {
    const commentsContainer = document.querySelector(containerSelector);
    if (!commentsContainer) {
        console.error("Komentar container tidak ditemukan");
        return;
    }

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) {
                    const newComments = node.querySelectorAll(commentsSelector);
                    newComments.forEach(detectHateSpeechFromNode);
                }
            });
        });
    });

    observer.observe(commentsContainer, { childList: true, subtree: true });
}

// Menambahkan style CSS untuk pewarnaan komentar
const style1 = document.createElement("style");
style1.textContent = `
    .highlight-low { background-color: #BDBDBD !important; } /* Abu-abu pudar */
    .highlight-mild { background-color: #FFD54F !important; } /* Kuning */
    .highlight-hate { background-color: #FF7043 !important; } /* Oranye kuat */
    .highlight-medium-low { background-color: #ff0000 !important; } /* Merah */
    .highlight-high { background-color: #860909 !important; } /* Merah pekat */
`;
document.head.appendChild(style1);

// Pewarnaan komentar berdasarkan probabilitas
function detectHateSpeechFromNode(commentNode) {
    const commentText = commentNode.innerHTML;

    if (commentNode.hasAttribute('data-highlighted')) return;

    const matchedComment = hateSpeechComments.find(apiComment => apiComment.original_comment === commentText);

    if (matchedComment) {
        const { predict_proba } = matchedComment;
        commentNode.setAttribute('data-highlighted', 'true');

        // Rentang pewarnaan
        if (predict_proba >= 0.50 && predict_proba < 0.60) {
            commentNode.classList.add('highlight-low'); // Abu-abu pudar
        } else if (predict_proba >= 0.60 && predict_proba < 0.70) {
            commentNode.classList.add('highlight-mild'); // Kuning
        } else if (predict_proba >= 0.70 && predict_proba < 0.80) {
            commentNode.classList.add('highlight-hate'); // Oranye kuat
        } else if (predict_proba >= 0.80 && predict_proba < 0.90) {
            commentNode.classList.add('highlight-medium-low'); // Merah
        } else if (predict_proba >= 0.90) {
            commentNode.classList.add('highlight-high'); // Merah pekat
        }

        console.log(`Pewarnaan: "${commentText}" dengan probabilitas: ${predict_proba}`);
        addValidationButtons(commentNode, commentText);
    }
}

// Menambahkan tombol validasi like/dislike
function addValidationButtons(commentNode, commentText) {
    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'inline-block';
    buttonContainer.style.marginLeft = '10px';

    const likeButton = document.createElement('button');
    likeButton.innerText = '👍';
    likeButton.onclick = () => sendValidation(commentText, 1);

    const dislikeButton = document.createElement('button');
    dislikeButton.innerText = '👎';
    dislikeButton.onclick = () => sendValidation(commentText, 0);

    buttonContainer.append(likeButton, dislikeButton);
    commentNode.parentElement.appendChild(buttonContainer);
}

// Mengirim validasi komentar ke server
function sendValidation(commentText, isLike) {
    fetch("http://127.0.0.1:8000/validate-comment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment_text: commentText, is_like: isLike, timestamp: new Date().toISOString() })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => console.log("Validation sent successfully:", data))
    .catch(error => console.error("Error sending validation:", error));
}

// Memproses komentar saat pertama kali memuat data API
function detectHateSpeech(hateSpeechComments) {
    document.querySelectorAll(commentsSelector).forEach(detectHateSpeechFromNode);
}

setInterval(checkUrlChange, 1000);