const panelToggle = document.querySelector("[data-panel-toggle]");
const panel = document.querySelector("[data-panel]");

if (panelToggle && panel) {
    const closePanel = () => {
        panel.hidden = true;
        panelToggle.setAttribute("aria-expanded", "false");
    };

    const openPanel = () => {
        panel.hidden = false;
        panelToggle.setAttribute("aria-expanded", "true");
    };

    panelToggle.addEventListener("click", () => {
        const expanded = panelToggle.getAttribute("aria-expanded") === "true";
        if (expanded) {
            closePanel();
        } else {
            openPanel();
        }
    });

    document.addEventListener("click", (event) => {
        if (!panel.hidden && !panel.contains(event.target) && !panelToggle.contains(event.target)) {
            closePanel();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closePanel();
        }
    });
}

const tagPickers = document.querySelectorAll("[data-tag-picker]");

tagPickers.forEach((picker) => {
    const toggle = picker.querySelector("[data-tag-picker-toggle]");
    const toggleHint = picker.querySelector("[data-tag-picker-toggle-hint]");
    const panelNode = picker.querySelector("[data-tag-picker-panel]");
    const searchInput = picker.querySelector("[data-tag-picker-search]");
    const clearButton = picker.querySelector("[data-tag-picker-clear]");
    const summaryNode = picker.querySelector("[data-tag-picker-summary]");
    const choices = Array.from(picker.querySelectorAll("[data-tag-choice]"));
    const inputs = choices
        .map((choice) => choice.querySelector("input[type='checkbox']"))
        .filter(Boolean);

    if (!toggle || !panelNode || !summaryNode) {
        return;
    }

    const setExpanded = (expanded) => {
        panelNode.hidden = !expanded;
        toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
        if (toggleHint) {
            toggleHint.textContent = expanded ? "收起" : "展开";
        }
        if (expanded && searchInput) {
            searchInput.focus();
        }
    };

    const getSelectedLabels = () =>
        choices
            .filter((choice) => {
                const input = choice.querySelector("input[type='checkbox']");
                return Boolean(input?.checked);
            })
            .map((choice) => choice.dataset.tagChoiceLabel || "")
            .filter(Boolean);

    const updateSummary = () => {
        const selectedLabels = getSelectedLabels();
        if (selectedLabels.length === 0) {
            summaryNode.textContent = "选择已有标签";
            return;
        }

        const preview = selectedLabels.slice(0, 3).join("、");
        const suffix =
            selectedLabels.length > 3
                ? ` 等 ${selectedLabels.length} 个`
                : ` 共 ${selectedLabels.length} 个`;
        summaryNode.textContent = `${preview}${suffix}`;
    };

    const applyFilter = () => {
        const keyword = searchInput?.value.trim().toLowerCase() || "";
        choices.forEach((choice) => {
            const label = (choice.dataset.tagChoiceLabel || "").toLowerCase();
            const input = choice.querySelector("input[type='checkbox']");
            const matched = !keyword || label.includes(keyword) || Boolean(input?.checked);
            choice.hidden = !matched;
        });
    };

    toggle.addEventListener("click", () => {
        setExpanded(panelNode.hidden);
    });

    searchInput?.addEventListener("input", applyFilter);

    clearButton?.addEventListener("click", () => {
        inputs.forEach((input) => {
            input.checked = false;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        });
        if (searchInput) {
            searchInput.value = "";
        }
        applyFilter();
        setExpanded(true);
    });

    inputs.forEach((input) => {
        input.addEventListener("change", () => {
            updateSummary();
            applyFilter();
        });
    });

    document.addEventListener("click", (event) => {
        if (!panelNode.hidden && !picker.contains(event.target)) {
            setExpanded(false);
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !panelNode.hidden) {
            setExpanded(false);
        }
    });

    updateSummary();
    applyFilter();
});

const toastStack = document.querySelector("[data-toast-stack]");

const escapeHtml = (value) =>
    String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

const showToast = (message, tone = "info") => {
    if (!toastStack || !message) {
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast toast--${tone}`;
    toast.textContent = message;
    toastStack.appendChild(toast);

    window.setTimeout(() => {
        toast.classList.add("is-leaving");
        window.setTimeout(() => {
            toast.remove();
        }, 240);
    }, 3000);
};

const metadataRoot = document.querySelector("[data-metadata-enrichment]");
const metadataModal = document.querySelector("[data-metadata-modal]");

if (metadataRoot && metadataModal) {
    const previewUrl = metadataRoot.dataset.previewUrl;
    const applyUrl = metadataRoot.dataset.applyUrl;
    const form = metadataRoot.closest("form");
    const providerSelect = metadataRoot.querySelector("[data-metadata-provider]");
    const previewTrigger = metadataRoot.querySelector("[data-metadata-preview-trigger]");
    const applyTrigger = metadataModal.querySelector("[data-metadata-apply-trigger]");
    const candidateNode = metadataModal.querySelector("[data-metadata-candidate]");
    const fieldsNode = metadataModal.querySelector("[data-metadata-fields]");
    const titleNode = metadataModal.querySelector("#metadata-modal-title");
    const closeButtons = metadataModal.querySelectorAll("[data-metadata-modal-close]");
    const csrfInput = form?.querySelector("input[name='csrfmiddlewaretoken']");
    const titleInput = form?.querySelector("[name='title']");
    const defaultApplyLabel = "确认填入";
    let currentPreview = null;

    const setPreviewLoading = (loading) => {
        if (!previewTrigger) {
            return;
        }
        previewTrigger.disabled = loading;
        previewTrigger.textContent = loading ? "获取中…" : "获取预览";
    };

    const setApplyLoading = (loading) => {
        if (!applyTrigger) {
            return;
        }
        applyTrigger.disabled = loading;
        if (loading) {
            applyTrigger.textContent = "填入中…";
            applyTrigger.classList.remove("button--muted");
            return;
        }
        syncApplyButtonState();
    };

    const openModal = () => {
        metadataModal.hidden = false;
        document.body.classList.add("has-modal-open");
    };

    const closeModal = () => {
        metadataModal.hidden = true;
        document.body.classList.remove("has-modal-open");
    };

    const formatValue = (value) => {
        if (!value) {
            return "空";
        }
        return value;
    };

    const getSelectedFieldNames = () =>
        Array.from(fieldsNode.querySelectorAll("input[type='checkbox']:checked")).map(
            (input) => input.value,
        );

    const syncApplyButtonState = () => {
        if (!applyTrigger) {
            return;
        }
        const selectedCount = getSelectedFieldNames().length;
        applyTrigger.disabled = false;
        applyTrigger.textContent =
            selectedCount > 0
                ? `${defaultApplyLabel}（${selectedCount}）`
                : `${defaultApplyLabel}（先勾选字段）`;
        applyTrigger.classList.toggle("button--muted", selectedCount === 0);
    };

    const patchFormValues = (values) => {
        Object.entries(values || {}).forEach(([fieldName, fieldValue]) => {
            const field = form?.querySelector(`[name='${fieldName}']`);
            if (!field) {
                return;
            }
            field.value = fieldValue;
            field.dispatchEvent(new Event("input", { bubbles: true }));
            field.dispatchEvent(new Event("change", { bubbles: true }));
        });
    };

    const renderCandidate = (preview) => {
        const candidate = preview.candidate || {};
        const metaParts = [
            candidate.author,
            candidate.translator ? `译者：${candidate.translator}` : "",
            candidate.publisher,
        ].filter(Boolean);
        const intro = candidate.intro || candidate.shortReview || "这个来源没有返回更多简介。";

        candidateNode.innerHTML = `
            <div class="metadata-candidate__cover">
                ${
                    candidate.coverImageUrl
                        ? `<img src="${escapeHtml(candidate.coverImageUrl)}" alt="${escapeHtml(candidate.title || "书籍封面")}">`
                        : `<span>${escapeHtml((candidate.title || "书").slice(0, 1))}</span>`
                }
            </div>
            <div class="metadata-candidate__body">
                <p class="section-label">${escapeHtml(preview.provider?.label || "外部来源")}</p>
                <h3>${escapeHtml(candidate.title || "未命名书籍")}</h3>
                ${
                    candidate.subtitle
                        ? `<p class="metadata-candidate__subtitle">${escapeHtml(candidate.subtitle)}</p>`
                        : ""
                }
                <p class="metadata-candidate__meta">${escapeHtml(metaParts.join(" · "))}</p>
                <p class="metadata-candidate__intro">${escapeHtml(intro)}</p>
            </div>
        `;
    };

    const renderFields = (preview) => {
        fieldsNode.innerHTML = (preview.fields || [])
            .map(
                (field) => `
                    <label class="metadata-field">
                        <span class="metadata-field__check">
                            <input
                                type="checkbox"
                                value="${escapeHtml(field.name)}"
                                ${field.defaultSelected ? "checked" : ""}
                            >
                            <strong>${escapeHtml(field.label)}</strong>
                        </span>
                        <span class="metadata-field__diff">
                            <span><em>当前</em>${escapeHtml(formatValue(field.current))}</span>
                            <span><em>新值</em>${escapeHtml(formatValue(field.incoming))}</span>
                        </span>
                    </label>
                `,
            )
            .join("");

        fieldsNode.querySelectorAll("input[type='checkbox']").forEach((input) => {
            input.addEventListener("change", syncApplyButtonState);
        });
        syncApplyButtonState();
    };

    const requestJson = async (url, payload) => {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfInput?.value || "",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({
            success: false,
            message: "请求失败，请稍后再试。",
        }));
        if (!response.ok) {
            throw new Error(data.message || "请求失败，请稍后再试。");
        }
        return data;
    };

    previewTrigger?.addEventListener("click", async () => {
        setPreviewLoading(true);
        try {
            const preview = await requestJson(previewUrl, {
                provider: providerSelect?.value || "weread",
                query: titleInput?.value || "",
            });

            if (preview.status !== "found") {
                showToast(preview.message || "暂时没有可补全的信息。");
                return;
            }

            currentPreview = preview;
            titleNode.textContent = `从${preview.provider?.label || "外部来源"}补全`;
            renderCandidate(preview);
            renderFields(preview);
            openModal();
        } catch (error) {
            showToast(error.message || "获取预览失败，请稍后再试。", "danger");
        } finally {
            setPreviewLoading(false);
        }
    });

    applyTrigger?.addEventListener("click", async () => {
        const selectedFields = getSelectedFieldNames();
        if (!currentPreview?.previewToken || selectedFields.length === 0) {
            showToast("请先选择至少一个要填入的字段。");
            return;
        }

        setApplyLoading(true);
        try {
            const result = await requestJson(applyUrl, {
                provider: providerSelect?.value || "weread",
                previewToken: currentPreview.previewToken,
                fields: selectedFields,
            });
            patchFormValues(result.values || {});
            closeModal();
            showToast(result.message || "已填入当前表单。", "success");
        } catch (error) {
            showToast(error.message || "填入失败，请重新获取预览。", "danger");
        } finally {
            setApplyLoading(false);
        }
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    metadataModal.addEventListener("click", (event) => {
        if (event.target === metadataModal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !metadataModal.hidden) {
            closeModal();
        }
    });
}

const bulkMetadataModal = document.querySelector("[data-bulk-metadata]");

if (bulkMetadataModal) {
    const bulkOpenButtons = document.querySelectorAll("[data-bulk-open]");
    const bulkCloseButtons = bulkMetadataModal.querySelectorAll("[data-bulk-close]");
    const bulkSearchInput = bulkMetadataModal.querySelector("[data-bulk-search]");
    const bulkSelectAllButton = bulkMetadataModal.querySelector("[data-bulk-select-all]");
    const bulkClearButton = bulkMetadataModal.querySelector("[data-bulk-clear]");
    const bulkSubmitButton = bulkMetadataModal.querySelector("[data-bulk-submit]");
    const bulkSelectionSummary = bulkMetadataModal.querySelector("[data-bulk-selection-summary]");
    const bulkBookChoices = Array.from(bulkMetadataModal.querySelectorAll("[data-bulk-book-choice]"));
    const bulkBookInputs = bulkBookChoices
        .map((choice) => choice.querySelector("[data-bulk-book]"))
        .filter(Boolean);
    const bulkResults = bulkMetadataModal.querySelector("[data-bulk-results]");
    const bulkResultsSummary = bulkMetadataModal.querySelector("[data-bulk-results-summary]");
    const bulkResultList = bulkMetadataModal.querySelector("[data-bulk-result-list]");
    const bulkStatusLabels = {
        updated: "已更新",
        unchanged: "已跳过",
        no_value: "无可用值",
        not_found: "未命中",
        unavailable: "暂不可用",
    };
    const csrfInput =
        document.querySelector(".editor-drawer__form input[name='csrfmiddlewaretoken']")
        || document.querySelector("input[name='csrfmiddlewaretoken']");
    const defaultBulkSubmitLabel = "开始批量更新";

    const requestJson = async (url, payload) => {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfInput?.value || "",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({
            success: false,
            message: "请求失败，请稍后再试。",
        }));
        if (!response.ok) {
            throw new Error(data.message || "请求失败，请稍后再试。");
        }
        return data;
    };

    const getSelectedBulkBookIds = () =>
        bulkBookInputs.filter((input) => input.checked).map((input) => input.value);

    const getVisibleBulkBookInputs = () =>
        bulkBookInputs.filter((input) => !input.closest("[data-bulk-book-choice]")?.hidden);

    const getSelectedBulkField = () =>
        bulkMetadataModal.querySelector("[data-bulk-field]:checked")?.value || "";

    const getSelectedBulkProvider = () =>
        bulkMetadataModal.querySelector("[data-bulk-provider]:checked")?.value || "";

    const openBulkModal = () => {
        bulkMetadataModal.hidden = false;
        document.body.classList.add("has-modal-open");
    };

    const closeBulkModal = () => {
        bulkMetadataModal.hidden = true;
        document.body.classList.remove("has-modal-open");
    };

    const updateBulkSubmitState = () => {
        const selectedCount = getSelectedBulkBookIds().length;
        if (!bulkSubmitButton) {
            return;
        }
        bulkSubmitButton.disabled = false;
        bulkSubmitButton.textContent =
            selectedCount > 0
                ? `${defaultBulkSubmitLabel}（${selectedCount}）`
                : `${defaultBulkSubmitLabel}（先选书籍）`;
        bulkSubmitButton.classList.toggle("button--muted", selectedCount === 0);
        if (bulkSelectionSummary) {
            bulkSelectionSummary.textContent =
                selectedCount > 0
                    ? `已选择 ${selectedCount} 本书，执行后会直接更新数据库。`
                    : "还未选择书籍";
        }
    };

    const filterBulkBooks = () => {
        const keyword = bulkSearchInput?.value.trim().toLowerCase() || "";
        bulkBookChoices.forEach((choice) => {
            const haystack = (choice.dataset.bulkBookText || "").toLowerCase();
            choice.hidden = Boolean(keyword) && !haystack.includes(keyword);
        });
    };

    const renderBulkResults = (payload) => {
        if (!bulkResults || !bulkResultsSummary || !bulkResultList) {
            return;
        }
        const summary = payload.summary || {};
        bulkResults.hidden = false;
        bulkResultsSummary.textContent =
            `共处理 ${summary.total || 0} 本，更新 ${summary.updated || 0} 本，`
            + `跳过相同 ${summary.unchanged || 0} 本，未命中 ${summary.not_found || 0} 本，`
            + `无值 ${summary.no_value || 0} 本，不可用 ${summary.unavailable || 0} 本。`;
        bulkResultList.innerHTML = (payload.results || [])
            .map(
                (row) => `
                    <article class="bulk-result-card">
                        <div class="bulk-result-card__header">
                            <strong>${escapeHtml(row.title || "未命名书籍")}</strong>
                            <span class="bulk-status bulk-status--${escapeHtml(row.status || "idle")}">
                                ${escapeHtml(bulkStatusLabels[row.status] || row.status || "未知")}
                            </span>
                        </div>
                        <p>${escapeHtml(row.message || "")}</p>
                    </article>
                `,
            )
            .join("");
    };

    const setBulkLoading = (loading) => {
        if (!bulkSubmitButton) {
            return;
        }
        bulkSubmitButton.disabled = loading;
        if (loading) {
            bulkSubmitButton.textContent = "批量更新中…";
            bulkSubmitButton.classList.remove("button--muted");
            return;
        }
        updateBulkSubmitState();
    };

    bulkOpenButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openBulkModal();
            updateBulkSubmitState();
        });
    });

    bulkCloseButtons.forEach((button) => {
        button.addEventListener("click", closeBulkModal);
    });

    bulkSearchInput?.addEventListener("input", filterBulkBooks);

    bulkSelectAllButton?.addEventListener("click", () => {
        getVisibleBulkBookInputs().forEach((input) => {
            input.checked = true;
        });
        updateBulkSubmitState();
    });

    bulkClearButton?.addEventListener("click", () => {
        bulkBookInputs.forEach((input) => {
            input.checked = false;
        });
        updateBulkSubmitState();
    });

    bulkBookInputs.forEach((input) => {
        input.addEventListener("change", updateBulkSubmitState);
    });

    bulkSubmitButton?.addEventListener("click", async () => {
        const bookIds = getSelectedBulkBookIds();
        if (bookIds.length === 0) {
            showToast("请先选择要批量更新的书籍。");
            return;
        }

        setBulkLoading(true);
        try {
            const payload = await requestJson(bulkMetadataModal.dataset.bulkUrl, {
                provider: getSelectedBulkProvider(),
                field: getSelectedBulkField(),
                bookIds,
            });
            renderBulkResults(payload);
            showToast(payload.message || "批量更新已完成。", payload.summary?.updated ? "success" : "info");
            if ((payload.summary?.updated || 0) > 0) {
                window.setTimeout(() => {
                    window.location.reload();
                }, 1200);
            }
        } catch (error) {
            showToast(error.message || "批量更新失败，请稍后再试。", "danger");
        } finally {
            setBulkLoading(false);
        }
    });

    bulkMetadataModal.addEventListener("click", (event) => {
        if (event.target === bulkMetadataModal) {
            closeBulkModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !bulkMetadataModal.hidden) {
            closeBulkModal();
        }
    });

    filterBulkBooks();
    updateBulkSubmitState();
}
