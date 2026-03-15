const readerRoot = document.querySelector("[data-epub-reader]");

if (readerRoot) {
    const viewer = readerRoot.querySelector("[data-reader-viewer]");
    const status = readerRoot.querySelector("[data-reader-status]");
    const progress = readerRoot.querySelector("[data-reader-progress]");
    const prevButton = readerRoot.querySelector("[data-reader-prev]");
    const nextButton = readerRoot.querySelector("[data-reader-next]");
    const bookUrl = readerRoot.dataset.bookUrl;

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

    const formatPercent = (value) => `${Math.max(0, Math.min(100, Math.round(value)))}%`;
    const setDownloadProgress = (message) => setProgress(`下载 ${message}`);
    const setReadingProgress = (message) => setProgress(`阅读位置 ${message}`);

    const downloadBook = async () => {
        const response = await fetch(bookUrl, {
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (!response.ok) {
            throw new Error(`文件请求失败：${response.status}`);
        }

        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("text/html")) {
            throw new Error("读取到的是网页而不是 EPUB 文件，可能是登录态失效。");
        }

        if (!response.body) {
            const fallbackBuffer = await response.arrayBuffer();
            setDownloadProgress("100%");
            return fallbackBuffer;
        }

        const total = Number(response.headers.get("content-length") || 0);
        const reader = response.body.getReader();
        const chunks = [];
        let received = 0;

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            chunks.push(value);
            received += value.length;
            if (total > 0) {
                setDownloadProgress(formatPercent((received / total) * 100));
            } else {
                setDownloadProgress(`${Math.round(received / 1024)} KB`);
            }
        }

        const merged = new Uint8Array(received);
        let offset = 0;
        for (const chunk of chunks) {
            merged.set(chunk, offset);
            offset += chunk.length;
        }
        if (total > 0) {
            setDownloadProgress("100%");
        }
        return merged.buffer;
    };

    const bootReader = async () => {
        if (!window.ePub) {
            setStatus("阅读器脚本没有加载成功，请刷新页面后重试。");
            return;
        }

        setStatus("正在下载 EPUB 文件…");
        setDownloadProgress("0%");

        try {
            const bookBuffer = await downloadBook();
            setStatus("文件下载完成，正在初始化阅读器…");

            const book = window.ePub(bookBuffer);
            const rendition = book.renderTo(viewer, {
                width: "100%",
                height: "100%",
                spread: "none",
            });

            book.opened
                .then(() => {
                    setStatus("正在解析目录与章节…");
                })
                .catch((error) => {
                    setStatus(`EPUB 打开失败：${error.message || error}`);
                });

            book.loaded.navigation
                .then(() => {
                    setStatus("目录已解析完成，正在打开正文…");
                })
                .catch((error) => {
                    setStatus(`目录解析失败：${error.message || error}`);
                });

            rendition.on("relocated", (location) => {
                const percentage = location?.start?.percentage;
                if (typeof percentage === "number") {
                    setReadingProgress(formatPercent(percentage * 100));
                }
            });

            await rendition.display();
            setStatus("EPUB 已加载，可以开始阅读。");
            setReadingProgress("0%");

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
        } catch (error) {
            setStatus(`EPUB 加载失败：${error.message || error}`);
            setProgress("读取失败");
        }
    };

    bootReader();
}
