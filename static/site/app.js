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
