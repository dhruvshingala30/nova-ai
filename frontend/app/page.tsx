"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Dynamic API Base URL resolution:
// Uses NEXT_PUBLIC_API_URL on Vercel deployment, falling back to localhost for local dev.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type NovaEvent = {
  event_type: string;
  content: string;
  data?: Record<string, unknown>;
};

type ChatTurn = {
  id: string;
  userMessage: string;
  events: NovaEvent[];
  assistantMessage?: string;
  activityExpanded: boolean;
};

type ChatSession = {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

type ConversationMessage = {
  role: "user" | "assistant";
  content: string;
};

function formatActivityEvent(event: NovaEvent) {
  switch (event.event_type) {
    case "session_updated":
      return {
        icon: "✏️",
        title: "Session Title",
        tone: "normal",
      };

    case "plan_started":
      return {
        icon: "🧐",
        title: "Analyzing Request",
        tone: "normal",
      };

    case "plan_created":
      return {
        icon: "🧠",
        title: "Planning",
        tone: "normal",
      };

    case "subtask_list":
      return {
        icon: "📋",
        title: "Task breakdown",
        tone: "normal",
      };

    case "subtask_dispatched":
      return {
        icon: "🚀",
        title: "Task dispatched",
        tone: "normal",
      };

    case "tool_invocation": {
      const tool = event.data?.tool;

      if (tool === "get_weather") {
        return {
          icon: "🌤️",
          title: "Weather",
          tone: "normal",
        };
      }

      if (tool === "search_web") {
        return {
          icon: "🔎",
          title: "Web Search",
          tone: "normal",
        };
      }

      if (tool === "run_python_code") {
        return {
          icon: "🐍",
          title: "Python",
          tone: "normal",
        };
      }

      if (
        tool === "knowledge_base_search" ||
        tool === "search_knowledge_base"
      ) {
        return {
          icon: "📄",
          title: "Knowledge Base",
          tone: "normal",
        };
      }

      if (tool === "inspect_image") {
        return {
          icon: "🖼️",
          title: "Image Inspection",
          tone: "normal",
        };
      }

      if (tool === "inspect_csv_schema") {
        return {
          icon: "📊",
          title: "CSV Inspection",
          tone: "normal",
        };
      }

      if (tool === "inspect_pdf_schema") {
        return {
          icon: "📄",
          title: "PDF Inspection",
          tone: "normal",
        };
      }

      if (tool === "list_workspace_files") {
        return {
          icon: "📁",
          title: "Workspace Files",
          tone: "normal",
        };
      }

      return {
        icon: "⚙️",
        title: "Tool execution",
        tone: "normal",
      };
    }

    case "tool_result":
      return {
        icon: "✓",
        title: "Tool completed",
        tone: "success",
      };

    case "agent_completed":
      return {
        icon: "✓",
        title: "Agent completed",
        tone: "success",
      };

    case "synthesis_started":
      return {
        icon: "◌",
        title: "Synthesizing",
        tone: "normal",
      };

    case "approval_required":
      return {
        icon: "⚠️",
        title: "Approval required",
        tone: "warning",
      };

    case "approval_granted":
      return {
        icon: "✓",
        title: "Approval granted",
        tone: "success",
      };

    case "approval_denied":
      return {
        icon: "✕",
        title: "Approval denied",
        tone: "danger",
      };

    case "subtask_skipped":
      return {
        icon: "⏭️",
        title: "Task skipped",
        tone: "warning",
      };

    default:
      return {
        icon: "•",
        title: event.event_type,
        tone: "normal",
      };
  }
}

function getProcessingStatus(events: NovaEvent[]) {
  const lastEvent = events[events.length - 1];

  if (!lastEvent) {
    return {
      icon: "◌",
      text: "Nova is starting...",
    };
  }

  switch (lastEvent.event_type) {
    case "session_updated":
      return {
        icon: "✏️",
        text: "Nova is updating the session...",
      };

    case "plan_started":
      return {
        icon: "🧐",
        text: "Nova is analyzing the request and drafting a plan...",
      };

    case "plan_created":
      return {
        icon: "🧠",
        text: "Nova is planning...",
      };

    case "subtask_list":
      return {
        icon: "📋",
        text: "Nova is breaking down the task...",
      };

    case "subtask_dispatched":
      return {
        icon: "🚀",
        text: "Nova is dispatching a task...",
      };

    case "tool_invocation": {
      const tool = lastEvent.data?.tool;

      switch (tool) {
        case "get_weather":
          return {
            icon: "🌤️",
            text: "Fetching weather...",
          };

        case "search_web":
          return {
            icon: "🔎",
            text: "Searching the web...",
          };

        case "run_python_code":
          return {
            icon: "🐍",
            text: "Running Python...",
          };

        case "inspect_image":
          return {
            icon: "🖼️",
            text: "Inspecting image...",
          };

        case "inspect_csv_schema":
          return {
            icon: "📊",
            text: "Inspecting CSV...",
          };

        case "inspect_pdf_schema":
          return {
            icon: "📄",
            text: "Inspecting PDF...",
          };

        case "list_workspace_files":
          return {
            icon: "📁",
            text: "Checking workspace files...",
          };

        case "knowledge_base_search":
        case "search_knowledge_base":
          return {
            icon: "📚",
            text: "Searching knowledge base...",
          };

        default:
          return {
            icon: "⚙️",
            text: "Executing a tool...",
          };
      }
    }

    case "tool_result":
      return {
        icon: "✓",
        text: "Processing tool result...",
      };

    case "approval_required":
      return {
        icon: "⚠️",
        text: "Waiting for your approval...",
      };

    case "approval_granted":
      return {
        icon: "✓",
        text: "Approval received. Continuing...",
      };

    case "approval_denied":
      return {
        icon: "✕",
        text: "Approval denied.",
      };

    case "agent_completed":
      return {
        icon: "✓",
        text: "Agent completed its task...",
      };

    case "synthesis_started":
      return {
        icon: "◌",
        text: "Nova is synthesizing the answer...",
      };

    default:
      return {
        icon: "⏳",
        text: "Nova is working...",
      };
  }
}

function getActiveAgent(events: NovaEvent[]) {
  for (let index = events.length - 1; index >= 0; index--) {
    const event = events[index];

    if (event.event_type === "subtask_dispatched") {
      return {
        agent:
          typeof event.data?.agent === "string" ? event.data.agent : "Agent",
        task: typeof event.data?.task === "string" ? event.data.task : "",
      };
    }

    if (event.event_type === "agent_completed") {
      return null;
    }

    if (event.event_type === "synthesis_started") {
      return {
        agent: "Supervisor",
        task: "Synthesizing specialist findings",
      };
    }
  }

  return null;
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  const [pendingApproval, setPendingApproval] = useState<{
    turnId: string;
    sessionId: string;
    reason: string;
    tool: string;
    code?: string;
  } | null>(null);

  const [isSubmittingApproval, setIsSubmittingApproval] = useState(false);

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations`);

      if (!response.ok) {
        throw new Error(`Failed to load conversations: ${response.status}`);
      }

      const data: ChatSession[] = await response.json();

      setSessions(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };

  const handleNewChat = () => {
    if (isRunning) return;

    setChatTurns([]);
    setSessionId(null);
    setMessage("");
    setPendingApproval(null);
    setIsSubmittingApproval(false);
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const submitApproval = async (approved: boolean) => {
    if (!pendingApproval || isSubmittingApproval) return;

    setIsSubmittingApproval(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/${pendingApproval.sessionId}/approval?approved=${approved}`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        throw new Error(`Approval request failed: ${response.status}`);
      }

      const data = await response.json();

      console.log("HITL decision submitted:", data);

      setPendingApproval(null);
    } catch (error) {
      console.error("Failed to submit HITL decision:", error);
    } finally {
      setIsSubmittingApproval(false);
    }
  };

  const loadConversation = async (selectedSessionId: string) => {
    if (isRunning) return;

    try {
      setIsRunning(false);
      setPendingApproval(null);
      setMessage("");

      const response = await fetch(
        `${API_BASE_URL}/api/conversations/${selectedSessionId}`,
      );

      if (!response.ok) {
        throw new Error(`Failed to load conversation: ${response.status}`);
      }

      const messages: ConversationMessage[] = await response.json();

      const turns: ChatTurn[] = [];

      let currentTurn: ChatTurn | null = null;

      for (const item of messages) {
        if (item.role === "user") {
          currentTurn = {
            id: crypto.randomUUID(),
            userMessage: item.content,
            events: [],
            activityExpanded: false,
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

  const sendMessage = async () => {
    if (!message.trim() || isRunning) return;

    const submittedMessage = message;
    const turnId = crypto.randomUUID();
    console.log("🆔 New turn:", turnId);
    console.log("💬 Session:", sessionId);

    // Create a new chat turn immediately
    setChatTurns((previous) => [
      ...previous,
      {
        id: turnId,
        userMessage: submittedMessage,
        events: [],
        activityExpanded: false,
      },
    ]);

    setMessage("");
    setIsRunning(true);
    setPendingApproval(null);
    setIsSubmittingApproval(false);

    // Reuse the same backend session for the whole conversation
    const currentSessionId = sessionId ?? crypto.randomUUID();

    try {
      // Start Nova
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: submittedMessage,
          session_id: currentSessionId,
        }),
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
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/chat/${data.session_id}/events`,
      );

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
        "final_answer",
      ];

      novaEvents.forEach((eventType) => {
        eventSource.addEventListener(eventType, async (event) => {
          const messageEvent = event as MessageEvent;

          try {
            const payload = JSON.parse(messageEvent.data);

            const novaEvent = payload?.event_response ?? payload;

            if (!novaEvent || !novaEvent.event_type) {
              console.warn(
                `Invalid Nova event received for [${eventType}]:`,
                payload,
              );

              return;
            }

            if (eventType === "approval_required") {
              const eventData = novaEvent.data ?? {};

              setPendingApproval({
                turnId,
                sessionId: data.session_id,
                reason:
                  typeof eventData.reason === "string"
                    ? eventData.reason
                    : novaEvent.content,
                tool:
                  typeof eventData.tool === "string"
                    ? eventData.tool
                    : "Unknown tool",
                code:
                  typeof eventData.code === "string"
                    ? eventData.code
                    : undefined,
              });
            }

            // 1. STREAMING CHUNKS: Append tokens directly to the assistant's message buffer
            else if (eventType === "synthesis_chunk") {
              setChatTurns((previous) =>
                previous.map((turn) =>
                  turn.id === turnId
                    ? {
                        ...turn,
                        assistantMessage:
                          (turn.assistantMessage ?? "") + novaEvent.content,
                      }
                    : turn,
                ),
              );
            }

            // 2. BACKGROUND TITLE UPDATE: Rename sidebar title without reloading
            else if (eventType === "session_updated") {
              const updatedTitle = novaEvent.data?.session_title as string;
              const targetSessionId =
                (novaEvent.data?.session_id as string) || data.session_id;

              if (updatedTitle) {
                setSessions((previous) =>
                  previous.map((s) =>
                    s.session_id === targetSessionId
                      ? { ...s, title: updatedTitle }
                      : s,
                  ),
                );
              }
            }

            // 3. final_answer completes this chat turn
            if (eventType === "final_answer") {
              streamCompleted = true;
              eventSource.close();

              setChatTurns((previous) =>
                previous.map((turn) =>
                  turn.id === turnId
                    ? {
                        ...turn,
                        assistantMessage: novaEvent.content,
                      }
                    : turn,
                ),
              );

              setIsRunning(false);
              loadSessions();
            } else {
              // Add the event to THIS chat turn
              setChatTurns((previous) =>
                previous.map((turn) =>
                  turn.id === turnId
                    ? {
                        ...turn,
                        events: [...turn.events, novaEvent as NovaEvent],
                      }
                    : turn,
                ),
              );
            }

            console.log(`Nova event [${eventType}]:`, novaEvent);
          } catch (error) {
            console.error(`Failed to parse Nova event [${eventType}]:`, error);
          }
        });
      });

      eventSource.onerror = (error) => {
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
      setChatTurns((previous) => previous.filter((turn) => turn.id !== turnId));
    }
  };

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-white text-gray-900">
      {/* 1. INDEPENDENT SIDEBAR */}
      <aside className="flex h-full w-64 shrink-0 flex-col border-r bg-gray-50">
        {/* Sidebar header */}
        <div className="border-b px-5 py-4">
          <h1 className="text-lg font-semibold tracking-tight text-gray-900">
            Nova
          </h1>
          <p className="text-xs text-gray-500">Multi-Agent AI Assistant</p>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            type="button"
            onClick={handleNewChat}
            disabled={isRunning}
            className="flex w-full items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span>+</span>
            <span>New Chat</span>
          </button>
        </div>

        {/* Sessions list with its own scrollbar */}
        <div className="flex-1 overflow-y-auto px-3 pb-4">
          <p className="px-2 py-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Conversations
          </p>

          <div className="space-y-1">
            {sessions.map((session) => (
              <button
                key={session.session_id}
                type="button"
                onClick={() => loadConversation(session.session_id)}
                disabled={isRunning}
                className={`w-full truncate rounded-lg px-3 py-2 text-left text-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${
                  session.session_id === sessionId
                    ? "bg-gray-200/80 font-medium text-gray-900"
                    : "text-gray-600 hover:bg-gray-200/50 hover:text-gray-900"
                }`}
              >
                {session.title}
              </button>
            ))}
          </div>
        </div>

        {/* Bottom Profile Badge */}
        <div className="border-t p-3">
          <div className="flex items-center gap-3 rounded-xl p-2 hover:bg-gray-100">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-900 text-xs font-bold text-white">
              N
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs font-medium text-gray-800">
                Nova Workspace
              </p>
              <p className="text-[10px] text-gray-400">Local Multi-Agent</p>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. INDEPENDENT MAIN CHAT WORKSPACE */}
      <section className="relative flex h-full flex-1 flex-col overflow-hidden bg-white">
        {chatTurns.length === 0 ? (
          /* ========================================================= */
          /* EMPTY STATE: CENTERED INPUT & GEMINI / CHATGPT TAGLINE   */
          /* ========================================================= */
          <div className="flex h-full flex-col items-center justify-center px-4 pb-20">
            <div className="w-full max-w-2xl text-center">
              <h2 className="mb-2 text-3xl font-semibold tracking-tight text-gray-800">
                Where should we begin?
              </h2>
              <p className="mb-8 text-sm text-gray-500">
                Ask a question, query documents, analyze datasets, or run
                research workflows.
              </p>

              {/* Centered Input Box */}
              <div className="relative flex items-center rounded-2xl border border-gray-200 bg-white p-2 shadow-sm focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-100">
                <input
                  type="text"
                  value={message}
                  disabled={isRunning}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Ask Nova anything..."
                  className="w-full bg-transparent px-4 py-3 text-base text-gray-800 placeholder-gray-400 outline-none"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={sendMessage}
                  disabled={isRunning || !message.trim()}
                  className="rounded-xl bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isRunning ? "Running..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* ========================================================= */
          /* ACTIVE CONVERSATION STATE: SCROLLABLE FEED + DOCKED BAR  */
          /* ========================================================= */
          <div className="flex h-full flex-col">
            {/* Scrollable messages container */}
            <div className="flex-1 overflow-y-auto px-6 py-8">
              <div className="mx-auto max-w-3xl space-y-8 pb-10">
                {chatTurns.map((turn) => (
                  <div key={turn.id} className="space-y-5">
                    {/* User message */}
                    <div className="flex justify-end">
                      <div className="max-w-2xl rounded-2xl bg-gray-900 px-5 py-3 text-white shadow-sm">
                        <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
                          You
                        </p>
                        <p className="whitespace-pre-wrap text-base leading-7">
                          {turn.userMessage}
                        </p>
                      </div>
                    </div>

                    {/* Nova activity feed */}
                    {turn.events.length > 0 && (
                      <div className="rounded-2xl border border-gray-200 bg-white shadow-sm">
                        {/* Activity header toggle */}
                        <button
                          type="button"
                          onClick={() =>
                            setChatTurns((previous) =>
                              previous.map((item) =>
                                item.id === turn.id
                                  ? {
                                      ...item,
                                      activityExpanded: !item.activityExpanded,
                                    }
                                  : item,
                              ),
                            )
                          }
                          className="flex w-full items-center justify-between px-5 py-3 text-left transition hover:bg-gray-50"
                        >
                          <div>
                            <p className="text-sm font-medium text-gray-700">
                              Nova Activity
                            </p>
                            <p className="text-xs text-gray-400">
                              {
                                turn.events.filter(
                                  (e) =>
                                    e.event_type !== "final_answer" &&
                                    e.event_type !== "synthesis_chunk",
                                ).length
                              }{" "}
                              actions recorded
                            </p>
                          </div>
                          <span className="text-base text-gray-400">
                            {turn.activityExpanded ? "⌃" : "⌄"}
                          </span>
                        </button>

                        {/* Active agent pill */}
                        {isRunning &&
                          turn.id === chatTurns[chatTurns.length - 1]?.id &&
                          (() => {
                            const activeAgent = getActiveAgent(turn.events);
                            if (!activeAgent) return null;

                            return (
                              <div className="border-t bg-gray-50/60 px-5 py-2.5">
                                <div className="flex items-center gap-3">
                                  <div className="flex h-7 w-7 items-center justify-center rounded-full border bg-white text-xs">
                                    🤖
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                                      Active Specialist
                                    </p>
                                    <p className="text-xs font-semibold text-gray-800">
                                      {activeAgent.agent}
                                    </p>
                                    {activeAgent.task && (
                                      <p className="truncate text-xs text-gray-500">
                                        {activeAgent.task}
                                      </p>
                                    )}
                                  </div>
                                  <div className="ml-auto flex gap-1">
                                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400" />
                                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400 [animation-delay:150ms]" />
                                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400 [animation-delay:300ms]" />
                                  </div>
                                </div>
                              </div>
                            );
                          })()}

                        {/* Expanded activity steps */}
                        {turn.activityExpanded && (
                          <div className="border-t px-5 py-4">
                            <div className="space-y-0">
                              {turn.events
                                .filter(
                                  (e) =>
                                    e.event_type !== "final_answer" &&
                                    e.event_type !== "synthesis_chunk",
                                )
                                .map((event, index, filteredEvents) => {
                                  const activity = formatActivityEvent(event);
                                  const isLast =
                                    index === filteredEvents.length - 1;

                                  return (
                                    <div
                                      key={`${event.event_type}-${index}`}
                                      className="relative flex gap-3"
                                    >
                                      <div className="flex w-6 shrink-0 flex-col items-center">
                                        <div
                                          className={`z-10 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border bg-white text-xs ${
                                            activity.tone === "warning"
                                              ? "border-amber-300"
                                              : activity.tone === "danger"
                                                ? "border-red-300"
                                                : activity.tone === "success"
                                                  ? "border-green-300"
                                                  : "border-gray-200"
                                          }`}
                                        >
                                          {activity.icon}
                                        </div>
                                        {!isLast && (
                                          <div className="w-px flex-1 bg-gray-200" />
                                        )}
                                      </div>

                                      <div
                                        className={`mb-3 min-w-0 flex-1 rounded-lg px-3 py-2 ${
                                          activity.tone === "warning"
                                            ? "bg-amber-50"
                                            : activity.tone === "danger"
                                              ? "bg-red-50"
                                              : activity.tone === "success"
                                                ? "bg-green-50"
                                                : "bg-gray-50/70"
                                        }`}
                                      >
                                        <p
                                          className={`text-xs font-semibold ${
                                            activity.tone === "warning"
                                              ? "text-amber-700"
                                              : activity.tone === "danger"
                                                ? "text-red-700"
                                                : activity.tone === "success"
                                                  ? "text-green-700"
                                                  : "text-gray-800"
                                          }`}
                                        >
                                          {activity.title}
                                        </p>
                                        <p className="mt-0.5 whitespace-pre-wrap text-xs leading-5 text-gray-600">
                                          {event.content}
                                        </p>
                                      </div>
                                    </div>
                                  );
                                })}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* HITL Card */}
                    {pendingApproval?.turnId === turn.id && (
                      <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-5 shadow-sm">
                        <div className="flex items-start gap-3">
                          <span className="mt-0.5 text-lg">⚠️</span>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold text-amber-900">
                              Approval Required
                            </p>
                            <p className="mt-0.5 text-xs text-amber-800">
                              Tool execution paused for operator confirmation:
                            </p>

                            <div className="mt-3 rounded-lg border border-amber-200 bg-white p-3">
                              <p className="text-xs font-semibold text-gray-800">
                                Tool: {pendingApproval.tool}
                              </p>
                              <p className="mt-1 whitespace-pre-wrap text-xs text-gray-600">
                                {pendingApproval.reason}
                              </p>
                            </div>

                            {pendingApproval.code && (
                              <details className="mt-2.5">
                                <summary className="cursor-pointer text-xs font-medium text-amber-800">
                                  View Python Script Preview
                                </summary>
                                <pre className="mt-2 overflow-x-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100">
                                  {pendingApproval.code}
                                </pre>
                              </details>
                            )}

                            <div className="mt-4 flex gap-2">
                              <button
                                type="button"
                                onClick={() => submitApproval(true)}
                                disabled={isSubmittingApproval}
                                className="rounded-lg bg-gray-900 px-4 py-2 text-xs font-medium text-white hover:bg-black disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {isSubmittingApproval
                                  ? "Submitting..."
                                  : "Approve"}
                              </button>
                              <button
                                type="button"
                                onClick={() => submitApproval(false)}
                                disabled={isSubmittingApproval}
                                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                Deny
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Agent Thinking Indicator */}
                    {turn.id === chatTurns[chatTurns.length - 1]?.id &&
                      isRunning &&
                      !turn.assistantMessage &&
                      (() => {
                        const status = getProcessingStatus(turn.events);
                        return (
                          <div className="flex justify-start">
                            <div className="rounded-2xl border border-gray-200 bg-white px-4 py-2.5 shadow-sm">
                              <p className="flex items-center gap-2 text-xs text-gray-500">
                                <span>{status.icon}</span>
                                <span>{status.text}</span>
                                <span className="animate-pulse">•••</span>
                              </p>
                            </div>
                          </div>
                        );
                      })()}

                    {/* Final Answer Display */}
                    {turn.assistantMessage && (
                      <div className="flex justify-start">
                        <div className="max-w-3xl rounded-2xl border border-gray-200 bg-white px-6 py-5 shadow-sm">
                          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
                            Nova
                          </p>
                          <div className="prose prose-sm max-w-none text-gray-800">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {turn.assistantMessage}
                            </ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Docked Input Form */}
            <div className="border-t bg-white px-6 py-4">
              <div className="mx-auto flex max-w-3xl items-center gap-2 rounded-2xl border border-gray-200 bg-white p-2 shadow-sm focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-100">
                <input
                  type="text"
                  value={message}
                  disabled={isRunning}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Ask Nova anything..."
                  className="flex-1 bg-transparent px-4 py-2 text-sm text-gray-800 placeholder-gray-400 outline-none"
                />
                <button
                  type="button"
                  onClick={sendMessage}
                  disabled={isRunning || !message.trim()}
                  className="rounded-xl bg-gray-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isRunning ? "Running..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
