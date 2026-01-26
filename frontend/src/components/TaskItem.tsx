/**
 * TaskItem component for displaying a single task.
 *
 * Shows task title, description, completion status, and action buttons.
 * Supports toggling completion, editing, and deleting.
 */

"use client";

import { type Task } from "@/lib/api";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit?: (task: Task) => void;
}

export default function TaskItem({ task, onToggle, onDelete, onEdit }: TaskItemProps) {
  return (
    <div className="flex items-start gap-4 p-4 border rounded-lg hover:shadow-md transition-shadow">
      {/* Checkbox for completion */}
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="mt-1 w-5 h-5 cursor-pointer"
        aria-label={`Mark "${task.title}" as ${task.completed ? "incomplete" : "complete"}`}
      />

      {/* Task content */}
      <div className="flex-1">
        <h3
          className={`text-lg font-medium ${
            task.completed ? "line-through text-gray-500" : "text-gray-900"
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p className="mt-1 text-sm text-gray-600">{task.description}</p>
        )}
        <p className="mt-2 text-xs text-gray-400">
          Created: {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        {onEdit && (
          <button
            onClick={() => onEdit(task)}
            className="px-3 py-1 text-sm text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors"
            aria-label={`Edit "${task.title}"`}
          >
            Edit
          </button>
        )}
        <button
          onClick={() => onDelete(task.id)}
          className="px-3 py-1 text-sm text-red-600 border border-red-600 rounded hover:bg-red-50 transition-colors"
          aria-label={`Delete "${task.title}"`}
        >
          Delete
        </button>
      </div>
    </div>
  );
}
