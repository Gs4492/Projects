export type AgentName = "planner" | "research" | "execution" | "critic" | "memory";
export type TaskStatus = "pending" | "in_progress" | "completed" | "needs_revision";
export type EventType = "log" | "task_update" | "artifact" | "retry" | "memory";

export interface TaskItem {
  id: string;
  title: string;
  owner: AgentName;
  status: TaskStatus;
  details: string;
  output: string | null;
  attempts: number;
}

export interface AgentLog {
  id: string;
  agent: AgentName;
  message: string;
  created_at: string;
}

export interface TimelineEvent {
  id: string;
  type: EventType;
  title: string;
  body: string;
  agent: AgentName | null;
  created_at: string;
}

export interface RunState {
  id: string;
  goal: string;
  status: "queued" | "running" | "completed";
  tasks: TaskItem[];
  logs: AgentLog[];
  timeline: TimelineEvent[];
  result: string | null;
  artifacts: Record<string, unknown>;
}
