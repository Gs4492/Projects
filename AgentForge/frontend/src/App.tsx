import { FormEvent, useEffect, useRef, useState } from "react";
import { RunState, TaskItem, TimelineEvent } from "./types";

const apiBase = "http://localhost:8000";

const emptyRun: RunState = {
  id: "",
  goal: "",
  status: "queued",
  tasks: [],
  logs: [],
  timeline: [],
  result: null,
  artifacts: {},
};

type ArtifactFile = { path: string; description: string; code: string };
type ApiRoute = { method: string; path: string; purpose: string; request: string; response: string };
type Decision = { title: string; details: string };

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function asObjectArray<T extends Record<string, string>>(value: unknown): T[] {
  return Array.isArray(value) ? (value.filter((item): item is T => typeof item === "object" && item !== null) as T[]) : [];
}

function App() {
  const [goal, setGoal] = useState("");
  const [run, setRun] = useState<RunState>(emptyRun);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => socketRef.current?.close();
  }, []);

  const connectToRun = (runId: string) => {
    socketRef.current?.close();
    const socket = new WebSocket(`ws://localhost:8000/ws/runs/${runId}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "snapshot" || message.type === "run") {
        setRun(message.payload);
      }
      if (message.type === "tasks") {
        setRun((current) => ({ ...current, tasks: message.payload as TaskItem[] }));
      }
      if (message.type === "log") {
        setRun((current) => ({ ...current, logs: [...current.logs, message.payload] }));
      }
      if (message.type === "timeline") {
        setRun((current) => ({ ...current, timeline: [...current.timeline, message.payload as TimelineEvent] }));
      }
      if (message.type === "run_completed") {
        setRun((current) => ({
          ...current,
          status: message.payload.status,
          result: message.payload.result,
          artifacts: message.payload.artifacts ?? current.artifacts,
          timeline: message.payload.timeline ?? current.timeline,
        }));
      }
    };

    socket.onopen = () => socket.send("subscribe");
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!goal.trim()) return;

    setIsSubmitting(true);
    const response = await fetch(`${apiBase}/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });
    const createdRun = await response.json();
    setRun({ ...createdRun, logs: [], timeline: [], artifacts: {}, tasks: createdRun.tasks ?? [] });
    connectToRun(createdRun.id);
    setIsSubmitting(false);
  };

  const executionOutput = (run.artifacts.execution_output ?? {}) as Record<string, unknown>;
  const architecture = asObjectArray<Decision>(executionOutput.architecture_decisions);
  const apiContract = asObjectArray<ApiRoute>(executionOutput.api_contract);
  const starterFiles = asObjectArray<ArtifactFile>(executionOutput.starter_files);
  const fileTree = asStringArray(executionOutput.file_tree);
  const testPlan = asStringArray(executionOutput.test_plan);
  const deployment = asStringArray(executionOutput.deployment_checklist);
  const risks = asStringArray(executionOutput.risks);
  const nextSteps = asStringArray(executionOutput.next_steps);
  const strengths = asStringArray(run.artifacts.critic_strengths);
  const improvements = asStringArray(run.artifacts.critic_improvements);
  const memoryLesson = typeof run.artifacts.memory_lesson === "string" ? run.artifacts.memory_lesson : null;
  const releaseReadiness = typeof run.artifacts.release_readiness === "string" ? run.artifacts.release_readiness : "prototype";
  const executionAttempts = Array.isArray(run.artifacts.execution_attempts) ? run.artifacts.execution_attempts.length : 0;
  const retryCount = run.timeline.filter((eventItem) => eventItem.type === "retry").length;
  const completedTasks = run.tasks.filter((task) => task.status === "completed").length;

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-topline">
          <div>
            <p className="eyebrow">AgentForge</p>
            <h1>Ship ideas with an AI delivery team</h1>
          </div>
          <span className={`status-pill status-${run.status}`}>{run.status || "idle"}</span>
        </div>
        <p className="hero-copy">
          Turn one goal into a concrete architecture, API design, starter files, quality review,
          retry loop, and reusable memory lesson.
        </p>
        <form className="goal-form" onSubmit={handleSubmit}>
          <textarea
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            placeholder="Design a production-ready Flask sentiment analysis app with backend architecture, frontend dashboard, REST API, model training approach, file structure, starter code, risks, and improvement suggestions."
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Running agents..." : "Start Run"}
          </button>
        </form>
        <div className="stats-grid">
          <div className="stat-card">
            <span>Completed Tasks</span>
            <strong>{completedTasks}/{run.tasks.length || 4}</strong>
          </div>
          <div className="stat-card">
            <span>Execution Drafts</span>
            <strong>{executionAttempts || 0}</strong>
          </div>
          <div className="stat-card">
            <span>Retry Requests</span>
            <strong>{retryCount}</strong>
          </div>
          <div className="stat-card">
            <span>Release Readiness</span>
            <strong>{releaseReadiness.split("_").join(" ")}</strong>
          </div>
        </div>
      </section>

      <section className="dashboard-grid primary-grid">
        <article className="panel deliverables-panel">
          <div className="panel-header">
            <h2>Concrete Deliverables</h2>
          </div>
          <p className="summary-copy">
            {typeof executionOutput.solution_summary === "string"
              ? executionOutput.solution_summary
              : "The execution agent will turn the plan into architecture, routes, files, and launch steps here."}
          </p>

          <div className="deliverable-grid">
            <section className="subpanel">
              <h3>Architecture Decisions</h3>
              {architecture.length === 0 ? <p className="empty-state">Waiting for architecture output.</p> : architecture.map((item) => (
                <div className="artifact-card" key={`${item.title}-${item.details}`}>
                  <strong>{item.title}</strong>
                  <p>{item.details}</p>
                </div>
              ))}
            </section>

            <section className="subpanel">
              <h3>API Contract</h3>
              {apiContract.length === 0 ? <p className="empty-state">Waiting for route specs.</p> : apiContract.map((route) => (
                <div className="artifact-card" key={`${route.method}-${route.path}`}>
                  <div className="route-chip-row">
                    <span className="route-method">{route.method}</span>
                    <span className="route-path">{route.path}</span>
                  </div>
                  <p>{route.purpose}</p>
                  <pre className="mini-code">Request: {route.request}{"\n"}Response: {route.response}</pre>
                </div>
              ))}
            </section>

            <section className="subpanel wide-subpanel">
              <h3>Starter Files</h3>
              {starterFiles.length === 0 ? <p className="empty-state">Waiting for starter files.</p> : starterFiles.map((file) => (
                <div className="artifact-card" key={file.path}>
                  <div className="file-heading">
                    <strong>{file.path}</strong>
                    <span>{file.description}</span>
                  </div>
                  <pre className="task-output">{file.code}</pre>
                </div>
              ))}
            </section>

            <section className="subpanel">
              <h3>File Tree</h3>
              {fileTree.length === 0 ? <p className="empty-state">Waiting for a file tree.</p> : <pre className="mini-code">{fileTree.join("\n")}</pre>}
            </section>

            <section className="subpanel">
              <h3>Test Plan</h3>
              {testPlan.length === 0 ? <p className="empty-state">Waiting for tests.</p> : <ul className="clean-list">{testPlan.map((item) => <li key={item}>{item}</li>)}</ul>}
            </section>

            <section className="subpanel">
              <h3>Deployment Checklist</h3>
              {deployment.length === 0 ? <p className="empty-state">Waiting for deployment checks.</p> : <ul className="clean-list">{deployment.map((item) => <li key={item}>{item}</li>)}</ul>}
            </section>

            <section className="subpanel">
              <h3>Risks</h3>
              {risks.length === 0 ? <p className="empty-state">Waiting for risk analysis.</p> : <ul className="clean-list">{risks.map((item) => <li key={item}>{item}</li>)}</ul>}
            </section>

            <section className="subpanel">
              <h3>Next Steps</h3>
              {nextSteps.length === 0 ? <p className="empty-state">Waiting for next steps.</p> : <ul className="clean-list">{nextSteps.map((item) => <li key={item}>{item}</li>)}</ul>}
            </section>
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Task Workflow</h2>
          </div>
          <div className="task-list compact-list">
            {run.tasks.length === 0 ? <p className="empty-state">No tasks yet. Start a run to generate the workflow.</p> : run.tasks.map((task) => (
              <div className="task-card" key={task.id}>
                <div className="task-topline">
                  <strong>{task.title}</strong>
                  <span className={`task-status task-${task.status}`}>{task.status}</span>
                </div>
                <p>{task.owner} agent · attempts: {task.attempts}</p>
                <p className="task-details">{task.details}</p>
                {task.output ? <p className="task-preview">{task.output}</p> : null}
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-grid secondary-grid">
        <article className="panel">
          <div className="panel-header">
            <h2>Critic Verdict</h2>
          </div>
          <p className="result-copy">{run.result ?? "The critic will summarize release readiness here."}</p>
          <div className="critic-grid">
            <div>
              <h3>Strengths</h3>
              {strengths.length === 0 ? <p className="empty-state">Strengths will appear after review.</p> : <ul className="clean-list">{strengths.map((item) => <li key={item}>{item}</li>)}</ul>}
            </div>
            <div>
              <h3>Improvements</h3>
              {improvements.length === 0 ? <p className="empty-state">No requested changes yet.</p> : <ul className="clean-list">{improvements.map((item) => <li key={item}>{item}</li>)}</ul>}
            </div>
          </div>
          <div className="lesson-card">
            <h3>Reusable Lesson</h3>
            <p>{memoryLesson ?? "The memory agent will save a reusable lesson here after the run completes."}</p>
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Timeline Playback</h2>
          </div>
          <div className="timeline-list">
            {run.timeline.length === 0 ? <p className="empty-state">Timeline events will appear here as the run evolves.</p> : run.timeline.map((eventItem) => (
              <div className={`timeline-card timeline-${eventItem.type}`} key={eventItem.id}>
                <div className="timeline-topline">
                  <strong>{eventItem.title}</strong>
                  <span>{eventItem.agent ?? "system"}</span>
                </div>
                <p>{eventItem.body}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-grid secondary-grid">
        <article className="panel">
          <div className="panel-header">
            <h2>Live Agent Logs</h2>
          </div>
          <div className="log-list">
            {run.logs.length === 0 ? <p className="empty-state">Logs will stream here when the run begins.</p> : run.logs.map((log) => (
              <div className="log-entry" key={log.id}>
                <span className="log-agent">{log.agent}</span>
                <p>{log.message}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Raw Artifacts</h2>
          </div>
          <pre className="task-output">{JSON.stringify(run.artifacts, null, 2)}</pre>
        </article>
      </section>
    </main>
  );
}

export default App;
