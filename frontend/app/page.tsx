"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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

function formatActivityEvent(event: NovaEvent) {
  switch (event.event_type) {
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
  
  const [pendingApproval, setPendingApproval] = useState<{
    turnId: string;
    sessionId: string;
    reason: string;
    tool: string;
    code?: string;
  } | null>(null);
    
  const [isSubmittingApproval, setIsSubmittingApproval] = useState(false);
    
  const submitApproval = async (approved: boolean) => {
    if (!pendingApproval || isSubmittingApproval) return;

    setIsSubmittingApproval(true);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/chat/${pendingApproval.sessionId}/approval?approved=${approved}`,
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
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
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

      console.log("Nova started:", data);

      // Connect to Nova's SSE stream
      const eventSource = new EventSource(
        `http://127.0.0.1:8000/api/chat/${data.session_id}/events`,
      );

      const novaEvents = [
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
        "final_answer",
      ];

      novaEvents.forEach((eventType) => {
        eventSource.addEventListener(eventType, (event) => {
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

            // final_answer completes this chat turn
            if (eventType === "final_answer") {
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
              eventSource.close();
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
    <main className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Nova</h1>

        <p className="text-sm text-gray-500">Multi-Agent AI Assistant</p>
      </header>

      {/* Main content */}
      <section className="flex flex-1 justify-center">
        <div className="w-full max-w-3xl px-6 py-10">
          {/* Conversation */}
          <div className="space-y-8">
            {chatTurns.map((turn) => (
              <div key={turn.id} className="space-y-5">
                {/* User message */}
                <div className="flex justify-end">
                  <div className="max-w-2xl rounded-2xl bg-black px-5 py-3 text-white">
                    <p className="mb-1 text-sm font-medium opacity-60">You</p>

                    <p className="whitespace-pre-wrap text-base leading-7">
                      {turn.userMessage}
                    </p>
                  </div>
                </div>

                {/* Nova activity */}
                {turn.events.length > 0 && (
                  <div className="rounded-2xl border">
                    {/* Activity header */}
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
                      className="flex w-full items-center justify-between px-5 py-4 text-left"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-500">
                          Nova Activity
                        </p>

                        <p className="text-xs text-gray-400">
                          {
                            turn.events.filter(
                              (event) => event.event_type !== "final_answer",
                            ).length
                          }{" "}
                          {turn.events.filter(
                            (event) => event.event_type !== "final_answer",
                          ).length === 1
                            ? "event"
                            : "events"}
                        </p>
                      </div>

                      <span className="text-lg text-gray-400">
                        {turn.activityExpanded ? "⌃" : "⌄"}
                      </span>
                    </button>

                    {/* Active agent */}
                    {isRunning &&
                      turn.id === chatTurns[chatTurns.length - 1]?.id &&
                      (() => {
                        const activeAgent = getActiveAgent(turn.events);

                        if (!activeAgent) return null;

                        return (
                          <div className="border-t bg-gray-50/50 px-5 py-3">
                            <div className="flex items-center gap-3">
                              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border bg-white text-sm">
                                🤖
                              </div>

                              <div className="min-w-0">
                                <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                                  Currently working
                                </p>

                                <p className="text-sm font-semibold text-gray-800">
                                  {activeAgent.agent}
                                </p>

                                {activeAgent.task && (
                                  <p className="mt-0.5 truncate text-xs text-gray-500">
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

                    {/* Activity details */}
                    {turn.activityExpanded && (
                      <div className="border-t px-5 py-4">
                        <div className="space-y-0">
                          {turn.events
                            .filter(
                              (event) => event.event_type !== "final_answer",
                            )
                            .map((event, index) => {
                              const activity = formatActivityEvent(event);
                              const isLast =
                                index ===
                                turn.events.filter(
                                  (item) => item.event_type !== "final_answer",
                                ).length -
                                  1;

                              return (
                                <div
                                  key={`${event.event_type}-${index}`}
                                  className="relative flex gap-3"
                                >
                                  {/* Timeline */}
                                  <div className="flex w-6 shrink-0 flex-col items-center">
                                    {/* Event icon */}
                                    <div
                                      className={`z-10 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border bg-white text-sm ${
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

                                    {/* Timeline connector */}
                                    {!isLast && (
                                      <div className="w-px flex-1 bg-gray-200" />
                                    )}
                                  </div>

                                  {/* Event content */}
                                  <div
                                    className={`mb-4 min-w-0 flex-1 rounded-lg px-3 py-2 ${
                                      activity.tone === "warning"
                                        ? "bg-amber-50"
                                        : activity.tone === "danger"
                                          ? "bg-red-50"
                                          : activity.tone === "success"
                                            ? "bg-green-50"
                                            : "bg-gray-50/50"
                                    }`}
                                  >
                                    <p
                                      className={`text-sm font-medium ${
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

                                    <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-500">
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

                {/* HITL Approval */}
                {pendingApproval?.turnId === turn.id && (
                  <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 text-lg">⚠️</div>

                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-amber-900">
                          Human approval required
                        </p>

                        <p className="mt-1 text-sm text-amber-800">
                          Nova wants permission to execute:
                        </p>

                        <div className="mt-3 rounded-lg border border-amber-200 bg-white p-3">
                          <p className="text-sm font-medium text-gray-800">
                            Tool: {pendingApproval.tool}
                          </p>

                          <p className="mt-1 whitespace-pre-wrap text-sm text-gray-600">
                            {pendingApproval.reason}
                          </p>
                        </div>

                        {pendingApproval.code && (
                          <details className="mt-3">
                            <summary className="cursor-pointer text-sm font-medium text-amber-800">
                              View code
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
                            className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {isSubmittingApproval ? "Submitting..." : "Approve"}
                          </button>

                          <button
                            type="button"
                            onClick={() => submitApproval(false)}
                            disabled={isSubmittingApproval}
                            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            Deny
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Nova working indicator */}
                {turn.id === chatTurns[chatTurns.length - 1]?.id &&
                  isRunning &&
                  (() => {
                    const status = getProcessingStatus(turn.events);

                    return (
                      <div className="flex justify-start">
                        <div className="rounded-2xl border px-5 py-3">
                          <p className="flex items-center gap-2 text-sm text-gray-500">
                            <span>{status.icon}</span>
                            <span>{status.text}</span>
                            <span className="animate-pulse">•••</span>
                          </p>
                        </div>
                      </div>
                    );
                  })()}

                {/* Nova answer */}
                {turn.assistantMessage && (
                  <div className="flex justify-start">
                    <div className="max-w-3xl rounded-2xl border px-5 py-4">
                      <p className="mb-1 text-sm font-medium text-gray-500">
                        Nova
                      </p>

                      <div className="prose prose-sm max-w-none">
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

          {/* Input */}
          <div className="mt-8 flex gap-2">
            <input
              type="text"
              value={message}
              disabled={isRunning}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  sendMessage();
                }
              }}
              placeholder="Ask Nova anything..."
              className="flex-1 rounded-xl border px-4 py-3 outline-none focus:ring-2"
            />

            <button
              onClick={sendMessage}
              disabled={isRunning}
              className="rounded-xl border px-5 py-3 font-medium disabled:opacity-50"
            >
              {isRunning ? "Running..." : "Send"}
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
