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


// 캐릭터 스택 노드용

app.registerExtension({
    name: "ComfyUI.NAIDGenerator.StackSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "V4CharacterPromptStackNAID") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const countWidget = this.widgets.find(w => w.name === "character_count");
                if (!countWidget) return;

                // 1. 최대 5개의 그리드를 생성하고 각 캐릭터 입력칸의 Y축 바로 밑에 삽입
                for (let i = 1; i <= 5; i++) {
                    const xW = this.widgets.find(w => w.name === `char_${i}_x`);
                    const yW = this.widgets.find(w => w.name === `char_${i}_y`);

                    if (xW && yW) {
                        const gridWidget = {
                            type: "NAI_GRID",
                            name: `grid_${i}`,
                            value: { x: xW.value, y: yW.value },
                            grid_x: 0, grid_y: 0, grid_size: 0,

                            draw: function (ctx, node, widgetWidth, widgetY, widgetHeight) {
                                if (this.type === "hidden") return; // 숨겨진 상태면 그리지 않음

                                const margin = 10;
                                const availableWidth = widgetWidth - margin * 2;
                                // 스택 노드가 너무 길어지지 않도록 미니 그리드 최대 높이를 140px로 제한
                                const size = Math.max(10, Math.min(availableWidth, 140));

                                this.grid_x = margin + (availableWidth - size) / 2; // 중앙 정렬
                                this.grid_y = widgetY;
                                this.grid_size = size;

                                ctx.fillStyle = "#111";
                                ctx.fillRect(this.grid_x, this.grid_y, size, size);

                                ctx.strokeStyle = "#333";
                                ctx.lineWidth = 1;
                                ctx.beginPath();
                                for (let j = 0; j <= 10; j++) {
                                    const pos = j * (size / 10);
                                    ctx.moveTo(this.grid_x + pos, this.grid_y);
                                    ctx.lineTo(this.grid_x + pos, this.grid_y + size);
                                    ctx.moveTo(this.grid_x, this.grid_y + pos);
                                    ctx.lineTo(this.grid_x + size, this.grid_y + pos);
                                }
                                ctx.stroke();

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

                                // 그리드 좌상단에 식별용 텍스트 표기
                                ctx.fillStyle = "#aaaaaa";
                                ctx.font = "12px Arial";
                                ctx.fillText(`Char ${i}`, this.grid_x + 4, this.grid_y + 14);
                            },
                            computeSize: function(width) {
                                if (this.type === "hidden") return [0, -4];
                                return [width, 150]; // 그리드가 차지할 세로 공간 할당
                            },
                            updateValue: function (pos, node) {
                                if (this.grid_size <= 0 || this.type === "hidden") return;
                                const size = this.grid_size;
                                let localX = pos[0] - this.grid_x;
                                let localY = pos[1] - this.grid_y;
                                localX = Math.max(0, Math.min(localX, size));
                                localY = Math.max(0, Math.min(localY, size));
                                let valX = Math.round((localX / size) * 10) / 10;
                                let valY = Math.round((localY / size) * 10) / 10;
                                this.value.x = valX;
                                this.value.y = valY;
                                xW.value = valX;
                                yW.value = valY;
                                node.setDirtyCanvas(true, true);
                            }
                        };

                        // Y 좌표 위젯 바로 밑에 그리드를 삽입
                        const yIndex = this.widgets.indexOf(yW);
                        this.widgets.splice(yIndex + 1, 0, gridWidget);

                        // 슬라이더 <-> 그리드 양방향 연동
                        const og_x_callback = xW.callback;
                        xW.callback = function(v) { gridWidget.value.x = v; node.setDirtyCanvas(true, true); if (og_x_callback) og_x_callback.call(xW, v); };
                        const og_y_callback = yW.callback;
                        yW.callback = function(v) { gridWidget.value.y = v; node.setDirtyCanvas(true, true); if (og_y_callback) og_y_callback.call(yW, v); };
                    }
                }

                // 2. 입력된 숫자(character_count)에 따라 위젯 숨김/표시 처리
                const updateVisibility = () => {
                    const count = countWidget.value;
                    for (let i = 1; i <= 5; i++) {
                        const isVisible = i <= count;
                        const wList = [
                            this.widgets.find(w => w.name === `char_${i}_caption`),
                            this.widgets.find(w => w.name === `char_${i}_negative`),
                            this.widgets.find(w => w.name === `char_${i}_x`),
                            this.widgets.find(w => w.name === `char_${i}_y`),
                            this.widgets.find(w => w.name === `grid_${i}`)
                        ];

                        wList.forEach(w => {
                            if (!w) return;
                            if (isVisible) {
                                if (w.origType) w.type = w.origType;
                                if (w.origComputeSize) w.computeSize = w.origComputeSize;
                            } else {
                                if (w.type !== "hidden") w.origType = w.type;
                                w.type = "hidden";
                                if (w.computeSize && !w.origComputeSize) w.origComputeSize = w.computeSize;
                                w.computeSize = () => [0, -4]; // 높이를 0으로 만들어 레이아웃에서 제거
                            }
                        });
                    }
                    this.setSize(this.computeSize()); // 노드 창 전체 크기 재조정
                };

                // 숫자 위젯이 조작될 때마다 UI 업데이트 발동
                const og_count_callback = countWidget.callback;
                countWidget.callback = function(v) {
                    if (og_count_callback) og_count_callback.call(countWidget, v);
                    updateVisibility();
                };

                // 노드 생성 직후 1번 실행하여 레이아웃 초기화
                setTimeout(updateVisibility, 50);
            };

            // 3. 다중 그리드 전용 마우스 이벤트 처리기
            const onMouseDown = nodeType.prototype.onMouseDown;
            nodeType.prototype.onMouseDown = function (e, pos, canvas) {
                for (let i = 1; i <= 5; i++) {
                    const gridWidget = this.widgets?.find(w => w.name === `grid_${i}`);
                    // 클릭된 위치가 현재 켜져있는 특정 그리드 안인지 확인
                    if (gridWidget && gridWidget.type !== "hidden" && gridWidget.grid_size > 0) {
                        if (pos[0] >= gridWidget.grid_x && pos[0] <= gridWidget.grid_x + gridWidget.grid_size &&
                            pos[1] >= gridWidget.grid_y && pos[1] <= gridWidget.grid_y + gridWidget.grid_size) {

                            this.dragging_grid = gridWidget; // 어떤 그리드를 조작 중인지 저장
                            canvas.node_capturing_input = this;
                            gridWidget.updateValue(pos, this);

                            const releaseDrag = () => {
                                this.dragging_grid = null;
                                if (canvas.node_capturing_input === this) canvas.node_capturing_input = null;
                                window.removeEventListener("mouseup", releaseDrag);
                                window.removeEventListener("pointerup", releaseDrag);
                            };
                            window.addEventListener("mouseup", releaseDrag);
                            window.addEventListener("pointerup", releaseDrag);

                            return true;
                        }
                    }
                }
                if (onMouseDown) return onMouseDown.apply(this, arguments);
                return false;
            };

            const onMouseMove = nodeType.prototype.onMouseMove;
            nodeType.prototype.onMouseMove = function (e, pos, canvas) {
                if (this.dragging_grid) {
                    if (e.buttons === 0) {
                        this.dragging_grid = null;
                        if (canvas.node_capturing_input === this) canvas.node_capturing_input = null;
                        return false;
                    }
                    this.dragging_grid.updateValue(pos, this);
                    return true;
                }
                if (onMouseMove) return onMouseMove.apply(this, arguments);
                return false;
            };

            const onMouseUp = nodeType.prototype.onMouseUp;
            nodeType.prototype.onMouseUp = function (e, pos, canvas) {
                if (this.dragging_grid) {
                    this.dragging_grid = null;
                    if (canvas.node_capturing_input === this) canvas.node_capturing_input = null;
                    return true;
                }
                if (onMouseUp) return onMouseUp.apply(this, arguments);
                return false;
            };
        }
    }
});