(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/app/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Home
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$markdown$2f$lib$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__Markdown__as__default$3e$__ = __turbopack_context__.i("[project]/node_modules/react-markdown/lib/index.js [app-client] (ecmascript) <export Markdown as default>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$remark$2d$gfm$2f$lib$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/remark-gfm/lib/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function formatActivityEvent(event) {
    switch(event.event_type){
        case "session_updated":
            return {
                icon: "✏️",
                title: "Session Title",
                tone: "normal"
            };
        case "plan_started":
            return {
                icon: "🧐",
                title: "Analyzing Request",
                tone: "normal"
            };
        case "plan_created":
            return {
                icon: "🧠",
                title: "Planning",
                tone: "normal"
            };
        case "subtask_list":
            return {
                icon: "📋",
                title: "Task breakdown",
                tone: "normal"
            };
        case "subtask_dispatched":
            return {
                icon: "🚀",
                title: "Task dispatched",
                tone: "normal"
            };
        case "tool_invocation":
            {
                const tool = event.data?.tool;
                if (tool === "get_weather") {
                    return {
                        icon: "🌤️",
                        title: "Weather",
                        tone: "normal"
                    };
                }
                if (tool === "search_web") {
                    return {
                        icon: "🔎",
                        title: "Web Search",
                        tone: "normal"
                    };
                }
                if (tool === "run_python_code") {
                    return {
                        icon: "🐍",
                        title: "Python",
                        tone: "normal"
                    };
                }
                if (tool === "knowledge_base_search" || tool === "search_knowledge_base") {
                    return {
                        icon: "📄",
                        title: "Knowledge Base",
                        tone: "normal"
                    };
                }
                if (tool === "inspect_image") {
                    return {
                        icon: "🖼️",
                        title: "Image Inspection",
                        tone: "normal"
                    };
                }
                if (tool === "inspect_csv_schema") {
                    return {
                        icon: "📊",
                        title: "CSV Inspection",
                        tone: "normal"
                    };
                }
                if (tool === "inspect_pdf_schema") {
                    return {
                        icon: "📄",
                        title: "PDF Inspection",
                        tone: "normal"
                    };
                }
                if (tool === "list_workspace_files") {
                    return {
                        icon: "📁",
                        title: "Workspace Files",
                        tone: "normal"
                    };
                }
                return {
                    icon: "⚙️",
                    title: "Tool execution",
                    tone: "normal"
                };
            }
        case "tool_result":
            return {
                icon: "✓",
                title: "Tool completed",
                tone: "success"
            };
        case "agent_completed":
            return {
                icon: "✓",
                title: "Agent completed",
                tone: "success"
            };
        case "synthesis_started":
            return {
                icon: "◌",
                title: "Synthesizing",
                tone: "normal"
            };
        case "approval_required":
            return {
                icon: "⚠️",
                title: "Approval required",
                tone: "warning"
            };
        case "approval_granted":
            return {
                icon: "✓",
                title: "Approval granted",
                tone: "success"
            };
        case "approval_denied":
            return {
                icon: "✕",
                title: "Approval denied",
                tone: "danger"
            };
        case "subtask_skipped":
            return {
                icon: "⏭️",
                title: "Task skipped",
                tone: "warning"
            };
        default:
            return {
                icon: "•",
                title: event.event_type,
                tone: "normal"
            };
    }
}
function getProcessingStatus(events) {
    const lastEvent = events[events.length - 1];
    if (!lastEvent) {
        return {
            icon: "◌",
            text: "Nova is starting..."
        };
    }
    switch(lastEvent.event_type){
        case "session_updated":
            return {
                icon: "✏️",
                text: "Nova is updating the session..."
            };
        case "plan_started":
            return {
                icon: "🧐",
                text: "Nova is analyzing the request and drafting a plan..."
            };
        case "plan_created":
            return {
                icon: "🧠",
                text: "Nova is planning..."
            };
        case "subtask_list":
            return {
                icon: "📋",
                text: "Nova is breaking down the task..."
            };
        case "subtask_dispatched":
            return {
                icon: "🚀",
                text: "Nova is dispatching a task..."
            };
        case "tool_invocation":
            {
                const tool = lastEvent.data?.tool;
                switch(tool){
                    case "get_weather":
                        return {
                            icon: "🌤️",
                            text: "Fetching weather..."
                        };
                    case "search_web":
                        return {
                            icon: "🔎",
                            text: "Searching the web..."
                        };
                    case "run_python_code":
                        return {
                            icon: "🐍",
                            text: "Running Python..."
                        };
                    case "inspect_image":
                        return {
                            icon: "🖼️",
                            text: "Inspecting image..."
                        };
                    case "inspect_csv_schema":
                        return {
                            icon: "📊",
                            text: "Inspecting CSV..."
                        };
                    case "inspect_pdf_schema":
                        return {
                            icon: "📄",
                            text: "Inspecting PDF..."
                        };
                    case "list_workspace_files":
                        return {
                            icon: "📁",
                            text: "Checking workspace files..."
                        };
                    case "knowledge_base_search":
                    case "search_knowledge_base":
                        return {
                            icon: "📚",
                            text: "Searching knowledge base..."
                        };
                    default:
                        return {
                            icon: "⚙️",
                            text: "Executing a tool..."
                        };
                }
            }
        case "tool_result":
            return {
                icon: "✓",
                text: "Processing tool result..."
            };
        case "approval_required":
            return {
                icon: "⚠️",
                text: "Waiting for your approval..."
            };
        case "approval_granted":
            return {
                icon: "✓",
                text: "Approval received. Continuing..."
            };
        case "approval_denied":
            return {
                icon: "✕",
                text: "Approval denied."
            };
        case "agent_completed":
            return {
                icon: "✓",
                text: "Agent completed its task..."
            };
        case "synthesis_started":
            return {
                icon: "◌",
                text: "Nova is synthesizing the answer..."
            };
        default:
            return {
                icon: "⏳",
                text: "Nova is working..."
            };
    }
}
function getActiveAgent(events) {
    for(let index = events.length - 1; index >= 0; index--){
        const event = events[index];
        if (event.event_type === "subtask_dispatched") {
            return {
                agent: typeof event.data?.agent === "string" ? event.data.agent : "Agent",
                task: typeof event.data?.task === "string" ? event.data.task : ""
            };
        }
        if (event.event_type === "agent_completed") {
            return null;
        }
        if (event.event_type === "synthesis_started") {
            return {
                agent: "Supervisor",
                task: "Synthesizing specialist findings"
            };
        }
    }
    return null;
}
function Home() {
    _s();
    const [message, setMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [chatTurns, setChatTurns] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isRunning, setIsRunning] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [sessionId, setSessionId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [sessions, setSessions] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [pendingApproval, setPendingApproval] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isSubmittingApproval, setIsSubmittingApproval] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const loadSessions = async ()=>{
        try {
            const response = await fetch("http://127.0.0.1:8000/api/conversations");
            if (!response.ok) {
                throw new Error(`Failed to load conversations: ${response.status}`);
            }
            const data = await response.json();
            setSessions(data);
        } catch (error) {
            console.error("Failed to load conversations:", error);
        }
    };
    const handleNewChat = ()=>{
        if (isRunning) return;
        setChatTurns([]);
        setSessionId(null);
        setMessage("");
        setPendingApproval(null);
        setIsSubmittingApproval(false);
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "Home.useEffect": ()=>{
            loadSessions();
        }
    }["Home.useEffect"], []);
    const submitApproval = async (approved)=>{
        if (!pendingApproval || isSubmittingApproval) return;
        setIsSubmittingApproval(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/chat/${pendingApproval.sessionId}/approval?approved=${approved}`, {
                method: "POST"
            });
            if (!response.ok) {
                throw new Error(`Approval request failed: ${response.status}`);
            }
            const data = await response.json();
            console.log("HITL decision submitted:", data);
            setPendingApproval(null);
        } catch (error) {
            console.error("Failed to submit HITL decision:", error);
        } finally{
            setIsSubmittingApproval(false);
        }
    };
    const loadConversation = async (selectedSessionId)=>{
        if (isRunning) return;
        try {
            setIsRunning(false);
            setPendingApproval(null);
            setMessage("");
            const response = await fetch(`http://127.0.0.1:8000/api/conversations/${selectedSessionId}`);
            if (!response.ok) {
                throw new Error(`Failed to load conversation: ${response.status}`);
            }
            const messages = await response.json();
            const turns = [];
            let currentTurn = null;
            for (const item of messages){
                if (item.role === "user") {
                    currentTurn = {
                        id: crypto.randomUUID(),
                        userMessage: item.content,
                        events: [],
                        activityExpanded: false
                    };
                    turns.push(currentTurn);
                } else if (item.role === "assistant") {
                    if (currentTurn) {
                        currentTurn.assistantMessage = item.content;
                    }
                }
            }
            setChatTurns(turns);
            setSessionId(selectedSessionId);
            console.log("Loaded conversation:", selectedSessionId);
            console.log("Messages:", messages);
        } catch (error) {
            console.error("Failed to load conversation:", error);
        }
    };
    const sendMessage = async ()=>{
        if (!message.trim() || isRunning) return;
        const submittedMessage = message;
        const turnId = crypto.randomUUID();
        console.log("🆔 New turn:", turnId);
        console.log("💬 Session:", sessionId);
        // Create a new chat turn immediately
        setChatTurns((previous)=>[
                ...previous,
                {
                    id: turnId,
                    userMessage: submittedMessage,
                    events: [],
                    activityExpanded: false
                }
            ]);
        setMessage("");
        setIsRunning(true);
        setPendingApproval(null);
        setIsSubmittingApproval(false);
        // Reuse the same backend session for the whole conversation
        const currentSessionId = sessionId ?? crypto.randomUUID();
        try {
            // Start Nova
            const response = await fetch("http://127.0.0.1:8000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: submittedMessage,
                    session_id: currentSessionId
                })
            });
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            const data = await response.json();
            // Store/reuse session ID
            setSessionId(data.session_id);
            // Instantly load the new session into the sidebar list!
            loadSessions();
            console.log("Nova started:", data);
            let streamCompleted = false;
            // Connect to Nova's SSE stream
            const eventSource = new EventSource(`http://127.0.0.1:8000/api/chat/${data.session_id}/events`);
            const novaEvents = [
                "plan_started",
                "plan_created",
                "subtask_list",
                "subtask_dispatched",
                "tool_invocation",
                "tool_result",
                "approval_required",
                "approval_granted",
                "approval_denied",
                "subtask_skipped",
                "agent_completed",
                "synthesis_started",
                "synthesis_chunk",
                "session_updated",
                "final_answer"
            ];
            novaEvents.forEach((eventType)=>{
                eventSource.addEventListener(eventType, async (event)=>{
                    const messageEvent = event;
                    try {
                        const payload = JSON.parse(messageEvent.data);
                        const novaEvent = payload?.event_response ?? payload;
                        if (!novaEvent || !novaEvent.event_type) {
                            console.warn(`Invalid Nova event received for [${eventType}]:`, payload);
                            return;
                        }
                        if (eventType === "approval_required") {
                            const eventData = novaEvent.data ?? {};
                            setPendingApproval({
                                turnId,
                                sessionId: data.session_id,
                                reason: typeof eventData.reason === "string" ? eventData.reason : novaEvent.content,
                                tool: typeof eventData.tool === "string" ? eventData.tool : "Unknown tool",
                                code: typeof eventData.code === "string" ? eventData.code : undefined
                            });
                        } else if (eventType === "synthesis_chunk") {
                            setChatTurns((previous)=>previous.map((turn)=>turn.id === turnId ? {
                                        ...turn,
                                        assistantMessage: (turn.assistantMessage ?? "") + novaEvent.content
                                    } : turn));
                        } else if (eventType === "session_updated") {
                            const updatedTitle = novaEvent.data?.session_title;
                            const targetSessionId = novaEvent.data?.session_id || data.session_id;
                            if (updatedTitle) {
                                setSessions((previous)=>previous.map((s)=>s.session_id === targetSessionId ? {
                                            ...s,
                                            title: updatedTitle
                                        } : s));
                            }
                        }
                        // 3. final_answer completes this chat turn
                        if (eventType === "final_answer") {
                            streamCompleted = true;
                            eventSource.close();
                            setChatTurns((previous)=>previous.map((turn)=>turn.id === turnId ? {
                                        ...turn,
                                        assistantMessage: novaEvent.content
                                    } : turn));
                            setIsRunning(false);
                            loadSessions();
                        } else {
                            // Add the event to THIS chat turn
                            setChatTurns((previous)=>previous.map((turn)=>turn.id === turnId ? {
                                        ...turn,
                                        events: [
                                            ...turn.events,
                                            novaEvent
                                        ]
                                    } : turn));
                        }
                        console.log(`Nova event [${eventType}]:`, novaEvent);
                    } catch (error) {
                        console.error(`Failed to parse Nova event [${eventType}]:`, error);
                    }
                });
            });
            eventSource.onerror = (error)=>{
                // If the stream already completed or is in CLOSED state, ignore the event
                if (streamCompleted || eventSource.readyState === EventSource.CLOSED) {
                    return;
                }
                console.error("Nova SSE error:", error);
                setIsRunning(false);
                eventSource.close();
            };
        } catch (error) {
            console.error("Failed to start Nova:", error);
            setIsRunning(false);
            // Remove the unfinished turn if the request itself failed
            setChatTurns((previous)=>previous.filter((turn)=>turn.id !== turnId));
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: "flex h-screen w-screen overflow-hidden bg-white text-gray-900",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
                className: "flex h-full w-64 shrink-0 flex-col border-r bg-gray-50",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "border-b px-5 py-4",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                className: "text-lg font-semibold tracking-tight text-gray-900",
                                children: "Nova"
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 718,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-xs text-gray-500",
                                children: "Multi-Agent AI Assistant"
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 721,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.tsx",
                        lineNumber: 717,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "p-3",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: handleNewChat,
                            disabled: isRunning,
                            className: "flex w-full items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    children: "+"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.tsx",
                                    lineNumber: 732,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    children: "New Chat"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.tsx",
                                    lineNumber: 733,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/page.tsx",
                            lineNumber: 726,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/app/page.tsx",
                        lineNumber: 725,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex-1 overflow-y-auto px-3 pb-4",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "px-2 py-2 text-xs font-semibold uppercase tracking-wider text-gray-400",
                                children: "Conversations"
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 739,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "space-y-1",
                                children: sessions.map((session)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: ()=>loadConversation(session.session_id),
                                        disabled: isRunning,
                                        className: `w-full truncate rounded-lg px-3 py-2 text-left text-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${session.session_id === sessionId ? "bg-gray-200/80 font-medium text-gray-900" : "text-gray-600 hover:bg-gray-200/50 hover:text-gray-900"}`,
                                        children: session.title
                                    }, session.session_id, false, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 745,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 743,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.tsx",
                        lineNumber: 738,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "border-t p-3",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center gap-3 rounded-xl p-2 hover:bg-gray-100",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex h-8 w-8 items-center justify-center rounded-full bg-gray-900 text-xs font-bold text-white",
                                    children: "N"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.tsx",
                                    lineNumber: 765,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "min-w-0",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                            className: "truncate text-xs font-medium text-gray-800",
                                            children: "Nova Workspace"
                                        }, void 0, false, {
                                            fileName: "[project]/app/page.tsx",
                                            lineNumber: 769,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                            className: "text-[10px] text-gray-400",
                                            children: "Local Multi-Agent"
                                        }, void 0, false, {
                                            fileName: "[project]/app/page.tsx",
                                            lineNumber: 772,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/app/page.tsx",
                                    lineNumber: 768,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/page.tsx",
                            lineNumber: 764,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/app/page.tsx",
                        lineNumber: 763,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.tsx",
                lineNumber: 715,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                className: "relative flex h-full flex-1 flex-col overflow-hidden bg-white",
                children: chatTurns.length === 0 ? /* ========================================================= */ /* EMPTY STATE: CENTERED INPUT & GEMINI / CHATGPT TAGLINE   */ /* ========================================================= */ /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex h-full flex-col items-center justify-center px-4 pb-20",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "w-full max-w-2xl text-center",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                className: "mb-2 text-3xl font-semibold tracking-tight text-gray-800",
                                children: "Where should we begin?"
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 786,
                                columnNumber: 15
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "mb-8 text-sm text-gray-500",
                                children: "Ask a question, query documents, analyze datasets, or run research workflows."
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 789,
                                columnNumber: 15
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "relative flex items-center rounded-2xl border border-gray-200 bg-white p-2 shadow-sm focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-100",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "text",
                                        value: message,
                                        disabled: isRunning,
                                        onChange: (e)=>setMessage(e.target.value),
                                        onKeyDown: (e)=>{
                                            if (e.key === "Enter" && !e.shiftKey) {
                                                e.preventDefault();
                                                sendMessage();
                                            }
                                        },
                                        placeholder: "Ask Nova anything...",
                                        className: "w-full bg-transparent px-4 py-3 text-base text-gray-800 placeholder-gray-400 outline-none",
                                        autoFocus: true
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 796,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: sendMessage,
                                        disabled: isRunning || !message.trim(),
                                        className: "rounded-xl bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-40",
                                        children: isRunning ? "Running..." : "Send"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 811,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 795,
                                columnNumber: 15
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.tsx",
                        lineNumber: 785,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/app/page.tsx",
                    lineNumber: 784,
                    columnNumber: 11
                }, this) : /* ========================================================= */ /* ACTIVE CONVERSATION STATE: SCROLLABLE FEED + DOCKED BAR  */ /* ========================================================= */ /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex h-full flex-col",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex-1 overflow-y-auto px-6 py-8",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mx-auto max-w-3xl space-y-8 pb-10",
                                children: chatTurns.map((turn)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "space-y-5",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "flex justify-end",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    className: "max-w-2xl rounded-2xl bg-gray-900 px-5 py-3 text-white shadow-sm",
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                            className: "mb-1 text-xs font-semibold uppercase tracking-wider text-gray-400",
                                                            children: "You"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 835,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                            className: "whitespace-pre-wrap text-base leading-7",
                                                            children: turn.userMessage
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 838,
                                                            columnNumber: 25
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/page.tsx",
                                                    lineNumber: 834,
                                                    columnNumber: 23
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/page.tsx",
                                                lineNumber: 833,
                                                columnNumber: 21
                                            }, this),
                                            turn.events.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "rounded-2xl border border-gray-200 bg-white shadow-sm",
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: ()=>setChatTurns((previous)=>previous.map((item)=>item.id === turn.id ? {
                                                                        ...item,
                                                                        activityExpanded: !item.activityExpanded
                                                                    } : item)),
                                                        className: "flex w-full items-center justify-between px-5 py-3 text-left transition hover:bg-gray-50",
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                children: [
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                        className: "text-sm font-medium text-gray-700",
                                                                        children: "Nova Activity"
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/page.tsx",
                                                                        lineNumber: 865,
                                                                        columnNumber: 29
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                        className: "text-xs text-gray-400",
                                                                        children: [
                                                                            turn.events.filter((e)=>e.event_type !== "final_answer" && e.event_type !== "synthesis_chunk").length,
                                                                            " ",
                                                                            "actions recorded"
                                                                        ]
                                                                    }, void 0, true, {
                                                                        fileName: "[project]/app/page.tsx",
                                                                        lineNumber: 868,
                                                                        columnNumber: 29
                                                                    }, this)
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/app/page.tsx",
                                                                lineNumber: 864,
                                                                columnNumber: 27
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                className: "text-base text-gray-400",
                                                                children: turn.activityExpanded ? "⌃" : "⌄"
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/page.tsx",
                                                                lineNumber: 879,
                                                                columnNumber: 27
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/app/page.tsx",
                                                        lineNumber: 848,
                                                        columnNumber: 25
                                                    }, this),
                                                    isRunning && turn.id === chatTurns[chatTurns.length - 1]?.id && (()=>{
                                                        const activeAgent = getActiveAgent(turn.events);
                                                        if (!activeAgent) return null;
                                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "border-t bg-gray-50/60 px-5 py-2.5",
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                className: "flex items-center gap-3",
                                                                children: [
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                        className: "flex h-7 w-7 items-center justify-center rounded-full border bg-white text-xs",
                                                                        children: "🤖"
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/page.tsx",
                                                                        lineNumber: 894,
                                                                        columnNumber: 35
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                        className: "min-w-0",
                                                                        children: [
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                                className: "text-[10px] font-semibold uppercase tracking-wider text-gray-400",
                                                                                children: "Active Specialist"
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 898,
                                                                                columnNumber: 37
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                                className: "text-xs font-semibold text-gray-800",
                                                                                children: activeAgent.agent
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 901,
                                                                                columnNumber: 37
                                                                            }, this),
                                                                            activeAgent.task && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                                className: "truncate text-xs text-gray-500",
                                                                                children: activeAgent.task
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 905,
                                                                                columnNumber: 39
                                                                            }, this)
                                                                        ]
                                                                    }, void 0, true, {
                                                                        fileName: "[project]/app/page.tsx",
                                                                        lineNumber: 897,
                                                                        columnNumber: 35
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                        className: "ml-auto flex gap-1",
                                                                        children: [
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                className: "h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400"
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 911,
                                                                                columnNumber: 37
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                className: "h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400 [animation-delay:150ms]"
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 912,
                                                                                columnNumber: 37
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                className: "h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400 [animation-delay:300ms]"
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/page.tsx",
                                                                                lineNumber: 913,
                                                                                columnNumber: 37
                                                                            }, this)
                                                                        ]
                                                                    }, void 0, true, {
                                                                        fileName: "[project]/app/page.tsx",
                                                                        lineNumber: 910,
                                                                        columnNumber: 35
                                                                    }, this)
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/app/page.tsx",
                                                                lineNumber: 893,
                                                                columnNumber: 33
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 892,
                                                            columnNumber: 31
                                                        }, this);
                                                    })(),
                                                    turn.activityExpanded && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        className: "border-t px-5 py-4",
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "space-y-0",
                                                            children: turn.events.filter((e)=>e.event_type !== "final_answer" && e.event_type !== "synthesis_chunk").map((event, index, filteredEvents)=>{
                                                                const activity = formatActivityEvent(event);
                                                                const isLast = index === filteredEvents.length - 1;
                                                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    className: "relative flex gap-3",
                                                                    children: [
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                            className: "flex w-6 shrink-0 flex-col items-center",
                                                                            children: [
                                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                    className: `z-10 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border bg-white text-xs ${activity.tone === "warning" ? "border-amber-300" : activity.tone === "danger" ? "border-red-300" : activity.tone === "success" ? "border-green-300" : "border-gray-200"}`,
                                                                                    children: activity.icon
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/app/page.tsx",
                                                                                    lineNumber: 941,
                                                                                    columnNumber: 41
                                                                                }, this),
                                                                                !isLast && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                    className: "w-px flex-1 bg-gray-200"
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/app/page.tsx",
                                                                                    lineNumber: 955,
                                                                                    columnNumber: 43
                                                                                }, this)
                                                                            ]
                                                                        }, void 0, true, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 940,
                                                                            columnNumber: 39
                                                                        }, this),
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                            className: `mb-3 min-w-0 flex-1 rounded-lg px-3 py-2 ${activity.tone === "warning" ? "bg-amber-50" : activity.tone === "danger" ? "bg-red-50" : activity.tone === "success" ? "bg-green-50" : "bg-gray-50/70"}`,
                                                                            children: [
                                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                                    className: `text-xs font-semibold ${activity.tone === "warning" ? "text-amber-700" : activity.tone === "danger" ? "text-red-700" : activity.tone === "success" ? "text-green-700" : "text-gray-800"}`,
                                                                                    children: activity.title
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/app/page.tsx",
                                                                                    lineNumber: 970,
                                                                                    columnNumber: 41
                                                                                }, this),
                                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                                    className: "mt-0.5 whitespace-pre-wrap text-xs leading-5 text-gray-600",
                                                                                    children: event.content
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/app/page.tsx",
                                                                                    lineNumber: 983,
                                                                                    columnNumber: 41
                                                                                }, this)
                                                                            ]
                                                                        }, void 0, true, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 959,
                                                                            columnNumber: 39
                                                                        }, this)
                                                                    ]
                                                                }, `${event.event_type}-${index}`, true, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 936,
                                                                    columnNumber: 37
                                                                }, this);
                                                            })
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 923,
                                                            columnNumber: 29
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/page.tsx",
                                                        lineNumber: 922,
                                                        columnNumber: 27
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/page.tsx",
                                                lineNumber: 846,
                                                columnNumber: 23
                                            }, this),
                                            pendingApproval?.turnId === turn.id && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "rounded-2xl border border-amber-200 bg-amber-50/60 p-5 shadow-sm",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    className: "flex items-start gap-3",
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            className: "mt-0.5 text-lg",
                                                            children: "⚠️"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 1000,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "min-w-0 flex-1",
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                    className: "text-sm font-semibold text-amber-900",
                                                                    children: "Approval Required"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1002,
                                                                    columnNumber: 29
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                    className: "mt-0.5 text-xs text-amber-800",
                                                                    children: "Tool execution paused for operator confirmation:"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1005,
                                                                    columnNumber: 29
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    className: "mt-3 rounded-lg border border-amber-200 bg-white p-3",
                                                                    children: [
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                            className: "text-xs font-semibold text-gray-800",
                                                                            children: [
                                                                                "Tool: ",
                                                                                pendingApproval.tool
                                                                            ]
                                                                        }, void 0, true, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1010,
                                                                            columnNumber: 31
                                                                        }, this),
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                                            className: "mt-1 whitespace-pre-wrap text-xs text-gray-600",
                                                                            children: pendingApproval.reason
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1013,
                                                                            columnNumber: 31
                                                                        }, this)
                                                                    ]
                                                                }, void 0, true, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1009,
                                                                    columnNumber: 29
                                                                }, this),
                                                                pendingApproval.code && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("details", {
                                                                    className: "mt-2.5",
                                                                    children: [
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("summary", {
                                                                            className: "cursor-pointer text-xs font-medium text-amber-800",
                                                                            children: "View Python Script Preview"
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1020,
                                                                            columnNumber: 33
                                                                        }, this),
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("pre", {
                                                                            className: "mt-2 overflow-x-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100",
                                                                            children: pendingApproval.code
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1023,
                                                                            columnNumber: 33
                                                                        }, this)
                                                                    ]
                                                                }, void 0, true, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1019,
                                                                    columnNumber: 31
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    className: "mt-4 flex gap-2",
                                                                    children: [
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                            type: "button",
                                                                            onClick: ()=>submitApproval(true),
                                                                            disabled: isSubmittingApproval,
                                                                            className: "rounded-lg bg-gray-900 px-4 py-2 text-xs font-medium text-white hover:bg-black disabled:cursor-not-allowed disabled:opacity-50",
                                                                            children: isSubmittingApproval ? "Submitting..." : "Approve"
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1030,
                                                                            columnNumber: 31
                                                                        }, this),
                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                            type: "button",
                                                                            onClick: ()=>submitApproval(false),
                                                                            disabled: isSubmittingApproval,
                                                                            className: "rounded-lg border border-gray-300 bg-white px-4 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50",
                                                                            children: "Deny"
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/page.tsx",
                                                                            lineNumber: 1040,
                                                                            columnNumber: 31
                                                                        }, this)
                                                                    ]
                                                                }, void 0, true, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1029,
                                                                    columnNumber: 29
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 1001,
                                                            columnNumber: 27
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/page.tsx",
                                                    lineNumber: 999,
                                                    columnNumber: 25
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/page.tsx",
                                                lineNumber: 998,
                                                columnNumber: 23
                                            }, this),
                                            turn.id === chatTurns[chatTurns.length - 1]?.id && isRunning && !turn.assistantMessage && // <--- Hides spinner as soon as the first chunk renders
                                            (()=>{
                                                const status = getProcessingStatus(turn.events);
                                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    className: "flex justify-start",
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        className: "rounded-2xl border border-gray-200 bg-white px-4 py-2.5 shadow-sm",
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                            className: "flex items-center gap-2 text-xs text-gray-500",
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    children: status.icon
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1064,
                                                                    columnNumber: 33
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    children: status.text
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1065,
                                                                    columnNumber: 33
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    className: "animate-pulse",
                                                                    children: "•••"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/page.tsx",
                                                                    lineNumber: 1066,
                                                                    columnNumber: 33
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 1063,
                                                            columnNumber: 31
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/page.tsx",
                                                        lineNumber: 1062,
                                                        columnNumber: 29
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/app/page.tsx",
                                                    lineNumber: 1061,
                                                    columnNumber: 27
                                                }, this);
                                            })(),
                                            turn.assistantMessage && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "flex justify-start",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    className: "max-w-3xl rounded-2xl border border-gray-200 bg-white px-6 py-5 shadow-sm",
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                            className: "mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400",
                                                            children: "Nova"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 1077,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "prose prose-sm max-w-none text-gray-800",
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$markdown$2f$lib$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__Markdown__as__default$3e$__["default"], {
                                                                remarkPlugins: [
                                                                    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$remark$2d$gfm$2f$lib$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"]
                                                                ],
                                                                children: turn.assistantMessage
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/page.tsx",
                                                                lineNumber: 1081,
                                                                columnNumber: 29
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/page.tsx",
                                                            lineNumber: 1080,
                                                            columnNumber: 27
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/page.tsx",
                                                    lineNumber: 1076,
                                                    columnNumber: 25
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/page.tsx",
                                                lineNumber: 1075,
                                                columnNumber: 23
                                            }, this)
                                        ]
                                    }, turn.id, true, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 831,
                                        columnNumber: 19
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 829,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/app/page.tsx",
                            lineNumber: 828,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "border-t bg-white px-6 py-4",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mx-auto flex max-w-3xl items-center gap-2 rounded-2xl border border-gray-200 bg-white p-2 shadow-sm focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-100",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "text",
                                        value: message,
                                        disabled: isRunning,
                                        onChange: (e)=>setMessage(e.target.value),
                                        onKeyDown: (e)=>{
                                            if (e.key === "Enter" && !e.shiftKey) {
                                                e.preventDefault();
                                                sendMessage();
                                            }
                                        },
                                        placeholder: "Ask Nova anything...",
                                        className: "flex-1 bg-transparent px-4 py-2 text-sm text-gray-800 placeholder-gray-400 outline-none"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 1096,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: sendMessage,
                                        disabled: isRunning || !message.trim(),
                                        className: "rounded-xl bg-gray-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-40",
                                        children: isRunning ? "Running..." : "Send"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.tsx",
                                        lineNumber: 1110,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/page.tsx",
                                lineNumber: 1095,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/app/page.tsx",
                            lineNumber: 1094,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/page.tsx",
                    lineNumber: 826,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/page.tsx",
                lineNumber: 779,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/page.tsx",
        lineNumber: 713,
        columnNumber: 5
    }, this);
}
_s(Home, "3cefiWUpMfDEpFZruYATsf56360=");
_c = Home;
var _c;
__turbopack_context__.k.register(_c, "Home");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=app_page_tsx_1s_43kl._.js.map