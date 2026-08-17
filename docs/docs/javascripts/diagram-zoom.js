(() => {
  const MIN_ZOOM = 0.5;
  const MAX_ZOOM = 3;
  const ZOOM_STEP = 0.25;

  let dialog;
  let viewport;
  let canvas;
  let level;
  let diagram;
  let placeholder;
  let originalStyle;
  let baseWidth;
  let baseHeight;
  let zoom = 1;
  let observer;

  const setZoom = (nextZoom) => {
    if (!diagram) {
      return;
    }

    zoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, nextZoom));
    const scaledWidth = baseWidth * zoom;
    const canvasWidth = Math.max(baseWidth, scaledWidth);

    diagram.style.position = "absolute";
    diagram.style.top = "0";
    diagram.style.left = `${Math.max(0, (canvasWidth - scaledWidth) / 2)}px`;
    diagram.style.transform = `scale(${zoom})`;
    canvas.style.width = `${canvasWidth}px`;
    canvas.style.height = `${baseHeight * zoom}px`;
    level.textContent = `${Math.round(zoom * 100)}%`;
  };

  const fitDiagram = () => {
    const horizontalZoom = (viewport.clientWidth - 32) / baseWidth;
    const verticalZoom = (viewport.clientHeight - 32) / baseHeight;

    setZoom(Math.min(1, horizontalZoom, verticalZoom));
    viewport.scrollTo(0, 0);
  };

  const restoreDiagram = () => {
    if (!diagram) {
      return;
    }

    if (originalStyle === null) {
      diagram.removeAttribute("style");
    } else {
      diagram.setAttribute("style", originalStyle);
    }

    if (placeholder?.isConnected) {
      placeholder.replaceWith(diagram);
    }

    canvas.replaceChildren();
    diagram = undefined;
    placeholder = undefined;
  };

  const createDialog = () => {
    if (dialog) {
      return;
    }

    dialog = document.createElement("dialog");
    dialog.className = "diagram-zoom";
    dialog.setAttribute("aria-label", "Enlarged diagram");
    dialog.innerHTML = `
      <div class="diagram-zoom__toolbar">
        <button type="button" data-action="zoom-out" aria-label="Zoom out">−</button>
        <span class="diagram-zoom__level" aria-live="polite">100%</span>
        <button type="button" data-action="zoom-in" aria-label="Zoom in">+</button>
        <button type="button" data-action="fit">Fit</button>
        <button type="button" data-action="reset">Reset</button>
        <button
          type="button"
          class="diagram-zoom__close"
          data-action="close"
          aria-label="Close enlarged diagram"
        >Close</button>
      </div>
      <div class="diagram-zoom__viewport">
        <div class="diagram-zoom__canvas"></div>
      </div>
    `;

    document.body.append(dialog);
    viewport = dialog.querySelector(".diagram-zoom__viewport");
    canvas = dialog.querySelector(".diagram-zoom__canvas");
    level = dialog.querySelector(".diagram-zoom__level");

    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
        return;
      }

      const action = event.target.closest("[data-action]")?.dataset.action;

      if (action === "zoom-out") {
        setZoom(zoom - ZOOM_STEP);
      } else if (action === "zoom-in") {
        setZoom(zoom + ZOOM_STEP);
      } else if (action === "fit") {
        fitDiagram();
      } else if (action === "reset") {
        setZoom(1);
        viewport.scrollTo(0, 0);
      } else if (action === "close") {
        dialog.close();
      }
    });

    viewport.addEventListener(
      "wheel",
      (event) => {
        if (!event.ctrlKey && !event.metaKey) {
          return;
        }

        event.preventDefault();
        setZoom(zoom + (event.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP));
      },
      { passive: false },
    );

    dialog.addEventListener("close", restoreDiagram);
  };

  const openDiagram = (source) => {
    if (diagram || !source.matches("div.mermaid")) {
      return;
    }

    createDialog();
    dialog.showModal();

    const bounds = source.getBoundingClientRect();
    placeholder = document.createElement("div");
    placeholder.style.height = `${bounds.height}px`;
    source.before(placeholder);

    diagram = source;
    originalStyle = source.getAttribute("style");
    baseWidth = Math.max(viewport.clientWidth - 32, bounds.width);

    canvas.append(source);
    source.style.width = `${baseWidth}px`;
    source.style.maxWidth = "none";
    source.style.transformOrigin = "top left";
    baseHeight = source.getBoundingClientRect().height;

    fitDiagram();
  };

  const enhanceDiagrams = () => {
    document.querySelectorAll("div.mermaid").forEach((source) => {
      if (source.dataset.zoomable) {
        return;
      }

      source.dataset.zoomable = "true";
      source.tabIndex = 0;
      source.setAttribute("role", "button");
      source.setAttribute("aria-label", "Open diagram in fullscreen viewer");

      source.addEventListener("click", () => openDiagram(source));
      source.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }

        event.preventDefault();
        openDiagram(source);
      });
    });
  };

  const start = () => {
    enhanceDiagrams();

    if (observer) {
      return;
    }

    observer = new MutationObserver(enhanceDiagrams);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  };

  if (typeof document$ === "undefined") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    document$.subscribe(start);
  }
})();
