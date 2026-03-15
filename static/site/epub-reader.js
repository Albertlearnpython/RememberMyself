const readerRoot = document.querySelector("[data-epub-reader]");

if (readerRoot && window.ePub) {
    const viewer = readerRoot.querySelector("[data-reader-viewer]");
    const status = readerRoot.querySelector("[data-reader-status]");
    const progress = readerRoot.querySelector("[data-reader-progress]");
    const prevButton = readerRoot.querySelector("[data-reader-prev]");
    const nextButton = readerRoot.querySelector("[data-reader-next]");
    const bookUrl = readerRoot.dataset.bookUrl;

    const book = window.ePub(bookUrl);
    const rendition = book.renderTo(viewer, {
        width: "100%",
        height: "100%",
        spread: "none",
    });

    const setStatus = (message) => {
        if (status) {
            status.textContent = message;
        }
    };

    const setProgress = (message) => {
        if (progress) {
            progress.textContent = message;
        }
    };

    setStatus("正在解析目录与章节…");
    rendition.display().then(() => {
        setStatus("EPUB 已加载，可以开始阅读。");
    }).catch(() => {
        setStatus("EPUB 加载失败，请稍后重试或直接下载文件。");
    });

    rendition.on("relocated", (location) => {
        if (!location || !location.start) {
            return;
        }
        const percentage = location.start.percentage;
        if (typeof percentage === "number") {
            setProgress(`${Math.round(percentage * 100)}%`);
        }
    });

    book.loaded.navigation.then(() => {
        setStatus("目录已解析完成。");
    }).catch(() => {
        setStatus("目录解析失败，但仍可尝试继续阅读。");
    });

    prevButton?.addEventListener("click", () => {
        rendition.prev();
    });

    nextButton?.addEventListener("click", () => {
        rendition.next();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") {
            rendition.prev();
        }
        if (event.key === "ArrowRight") {
            rendition.next();
        }
    });
}
