import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.NAIDGenerator.GridSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "V4CharacterPromptOptionNAID") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                const xWidget = this.widgets.find(w => w.name === "center_x");
                const yWidget = this.widgets.find(w => w.name === "center_y");

                if (!xWidget || !yWidget) return;

                const gridWidget = {
                    type: "NAI_GRID",
                    name: "Position Selector",
                    value: { x: xWidget.value, y: yWidget.value },

                    grid_x: 0,
                    grid_y: 0,
                    grid_size: 0,

                    draw: function (ctx, node, widgetWidth, widgetY, widgetHeight) {
                        const margin = 10;
                        const availableWidth = widgetWidth - margin * 2;
                        const availableHeight = node.size[1] - widgetY - margin;

                        const size = Math.max(10, Math.min(availableWidth, availableHeight));

                        this.grid_x = margin;
                        this.grid_y = widgetY;
                        this.grid_size = size;

                        // 배경
                        ctx.fillStyle = "#111";
                        ctx.fillRect(this.grid_x, this.grid_y, size, size);

                        // 0.1 단위 그리드 선
                        ctx.strokeStyle = "#333";
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        for (let i = 0; i <= 10; i++) {
                            const pos = i * (size / 10);
                            ctx.moveTo(this.grid_x + pos, this.grid_y);
                            ctx.lineTo(this.grid_x + pos, this.grid_y + size);
                            ctx.moveTo(this.grid_x, this.grid_y + pos);
                            ctx.lineTo(this.grid_x + size, this.grid_y + pos);
                        }
                        ctx.stroke();

                        // 좌표점(마커) 계산 및 드로잉
                        const px = this.grid_x + (this.value.x * size);
                        const py = this.grid_y + (this.value.y * size);

                        ctx.fillStyle = "#ff4444";
                        ctx.beginPath();
                        ctx.arc(px, py, 4, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.strokeStyle = "#ff8888";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.moveTo(px - 8, py);
                        ctx.lineTo(px + 8, py);
                        ctx.moveTo(px, py - 8);
                        ctx.lineTo(px, py + 8);
                        ctx.stroke();
                    },

                    computeSize: function (width) {
                        return [width, width];
                    },

                    updateValue: function (pos, node) {
                        if (this.grid_size <= 0) return;
                        const size = this.grid_size;

                        let localX = pos[0] - this.grid_x;
                        let localY = pos[1] - this.grid_y;

                        localX = Math.max(0, Math.min(localX, size));
                        localY = Math.max(0, Math.min(localY, size));

                        let valX = Math.round((localX / size) * 10) / 10;
                        let valY = Math.round((localY / size) * 10) / 10;

                        this.value.x = valX;
                        this.value.y = valY;

                        xWidget.value = valX;
                        yWidget.value = valY;

                        node.setDirtyCanvas(true, true);
                    }
                };

                this.addCustomWidget(gridWidget);

                const og_x_callback = xWidget.callback;
                xWidget.callback = function(v) {
                    gridWidget.value.x = v;
                    node.setDirtyCanvas(true, true);
                    if (og_x_callback) og_x_callback.call(xWidget, v);
                };

                const og_y_callback = yWidget.callback;
                yWidget.callback = function(v) {
                    gridWidget.value.y = v;
                    node.setDirtyCanvas(true, true);
                    if (og_y_callback) og_y_callback.call(yWidget, v);
                };
            };

            // ========================================================
            // 글로벌 마우스 이벤트 캡처
            // ========================================================

            const onMouseDown = nodeType.prototype.onMouseDown;
            nodeType.prototype.onMouseDown = function (e, pos, canvas) {
                const gridWidget = this.widgets?.find(w => w.name === "Position Selector");
                if (gridWidget && gridWidget.grid_size > 0) {
                    if (pos[0] >= gridWidget.grid_x && pos[0] <= gridWidget.grid_x + gridWidget.grid_size &&
                        pos[1] >= gridWidget.grid_y && pos[1] <= gridWidget.grid_y + gridWidget.grid_size) {

                        this.dragging_grid = true;
                        canvas.node_capturing_input = this;
                        gridWidget.updateValue(pos, this);

                        const releaseDrag = () => {
                            this.dragging_grid = false;
                            if (canvas.node_capturing_input === this) {
                                canvas.node_capturing_input = null;
                            }
                            window.removeEventListener("mouseup", releaseDrag);
                            window.removeEventListener("pointerup", releaseDrag);
                        };
                        window.addEventListener("mouseup", releaseDrag);
                        window.addEventListener("pointerup", releaseDrag);

                        return true;
                    }
                }
                if (onMouseDown) return onMouseDown.apply(this, arguments);
                return false;
            };

            const onMouseMove = nodeType.prototype.onMouseMove;
            nodeType.prototype.onMouseMove = function (e, pos, canvas) {
                if (this.dragging_grid) {
                    if (e.buttons === 0) {
                        this.dragging_grid = false;
                        if (canvas.node_capturing_input === this) {
                            canvas.node_capturing_input = null;
                        }
                        return false;
                    }

                    const gridWidget = this.widgets?.find(w => w.name === "Position Selector");
                    if (gridWidget) {
                        gridWidget.updateValue(pos, this);
                    }
                    return true;
                }
                if (onMouseMove) return onMouseMove.apply(this, arguments);
                return false;
            };

            const onMouseUp = nodeType.prototype.onMouseUp;
            nodeType.prototype.onMouseUp = function (e, pos, canvas) {
                if (this.dragging_grid) {
                    this.dragging_grid = false;
                    if (canvas.node_capturing_input === this) {
                        canvas.node_capturing_input = null;
                    }
                    return true;
                }
                if (onMouseUp) return onMouseUp.apply(this, arguments);
                return false;
            };
        }
    }
});