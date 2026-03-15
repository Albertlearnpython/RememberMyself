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
