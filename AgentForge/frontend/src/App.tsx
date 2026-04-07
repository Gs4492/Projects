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

function App() {
  const [goal, setGoal] = useState("");
  const [run, setRun] = useState<RunState>(emptyRun);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => {
      socketRef.current?.close();
    };
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
        setRun((current) => ({
          ...current,
          timeline: [...current.timeline, message.payload as TimelineEvent],
        }));
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

    socket.onopen = () => {
      socket.send("subscribe");
    };
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!goal.trim()) {
      return;
    }

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

  const memoryLesson = typeof run.artifacts.memory_lesson === "string" ? run.artifacts.memory_lesson : null;

  return (
    <main className="page-shell">
      <section className="hero-card">
        <p className="eyebrow">AgentForge</p>
        <h1>Agentic AI workflow dashboard</h1>
        <p className="hero-copy">
          Enter a product or software goal and watch planner, research, execution,
          critic, and memory agents coordinate in real time.
        </p>
        <form className="goal-form" onSubmit={handleSubmit}>
          <textarea
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            placeholder="Build me a Flask sentiment analysis app with a simple UI."
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Starting..." : "Start Run"}
          </button>
        </form>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel-header">
            <h2>Task Workflow</h2>
            <span className={`status-pill status-${run.status}`}>{run.status || "idle"}</span>
          </div>
          <div className="task-list">
            {run.tasks.length === 0 ? (
              <p className="empty-state">No tasks yet. Start a run to generate the workflow.</p>
            ) : (
              run.tasks.map((task) => (
                <div className="task-card" key={task.id}>
                  <div className="task-topline">
                    <strong>{task.title}</strong>
                    <span className={`task-status task-${task.status}`}>{task.status}</span>
                  </div>
                  <p>{task.owner} agent · attempts: {task.attempts}</p>
                  <p className="task-details">{task.details}</p>
                  {task.output ? <pre className="task-output">{task.output}</pre> : null}
                </div>
              ))
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Timeline Playback</h2>
          </div>
          <div className="timeline-list">
            {run.timeline.length === 0 ? (
              <p className="empty-state">Timeline events will appear here as the run evolves.</p>
            ) : (
              run.timeline.map((eventItem) => (
                <div className={`timeline-card timeline-${eventItem.type}`} key={eventItem.id}>
                  <div className="timeline-topline">
                    <strong>{eventItem.title}</strong>
                    <span>{eventItem.agent ?? "system"}</span>
                  </div>
                  <p>{eventItem.body}</p>
                </div>
              ))
            )}
          </div>
        </article>
      </section>

      <section className="dashboard-grid secondary-grid">
        <article className="panel">
          <div className="panel-header">
            <h2>Live Agent Logs</h2>
          </div>
          <div className="log-list">
            {run.logs.length === 0 ? (
              <p className="empty-state">Logs will stream here when the run begins.</p>
            ) : (
              run.logs.map((log) => (
                <div className="log-entry" key={log.id}>
                  <span className="log-agent">{log.agent}</span>
                  <p>{log.message}</p>
                </div>
              ))
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Reusable Lesson</h2>
          </div>
          <p className="result-copy">
            {memoryLesson ?? "The memory agent will save one reusable lesson here after the run completes."}
          </p>
          {Object.keys(run.artifacts).length > 0 ? (
            <div className="artifact-block">
              <h3>Agent Artifacts</h3>
              <pre className="task-output">{JSON.stringify(run.artifacts, null, 2)}</pre>
            </div>
          ) : null}
        </article>
      </section>

      <section className="panel result-panel">
        <div className="panel-header">
          <h2>Run Result</h2>
        </div>
        <p className="result-copy">
          {run.result ?? "The final reviewed result will appear here after the critic signs off."}
        </p>
      </section>
    </main>
  );
}

export default App;
