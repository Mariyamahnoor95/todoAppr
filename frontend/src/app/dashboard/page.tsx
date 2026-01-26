"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import { type Task } from "@/lib/api";

/**
 * Dashboard page - Protected route with task management
 *
 * Displays user tasks with create, update, delete, and toggle functionality.
 * Supports filtering by completion status.
 */
export default function DashboardPage() {
  const { user, isAuthenticated, logout } = useAuth();
  const { tasks, loading, error, fetchTasks, createTask, updateTask, toggleTask, deleteTask } = useTasks();
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push("/");
    }
  }, [isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated) {
      const filterParams =
        filter === "active" ? { completed: false } : filter === "completed" ? { completed: true } : undefined;
      fetchTasks(filterParams);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, filter]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  const handleCreateTask = async (title: string, description?: string) => {
    const task = await createTask(title, description);
    if (task) {
      setShowForm(false);
    }
  };

  const handleEditTask = async (title: string, description?: string) => {
    if (editingTask) {
      const updated = await updateTask(editingTask.id, { title, description });
      if (updated) {
        setEditingTask(null);
        setShowForm(false);
      }
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  const completedCount = tasks.filter((t) => t.completed).length;
  const activeCount = tasks.filter((t) => !t.completed).length;

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <p className="text-gray-600 mt-1">{user.email}</p>
          </div>
          <Button onClick={logout} variant="outline">
            Logout
          </Button>
        </div>

        {/* Task Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Total Tasks</p>
            <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Active</p>
            <p className="text-2xl font-bold text-blue-600">{activeCount}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Completed</p>
            <p className="text-2xl font-bold text-green-600">{completedCount}</p>
          </div>
        </div>

        {/* Add Task Button */}
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="w-full mb-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + Add New Task
          </button>
        )}

        {/* Task Form */}
        {showForm && (
          <div className="mb-6 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">
              {editingTask ? "Edit Task" : "Create New Task"}
            </h2>
            <TaskForm
              task={editingTask}
              onSubmit={editingTask ? handleEditTask : handleCreateTask}
              onCancel={handleCancelForm}
              submitLabel={editingTask ? "Update Task" : "Create Task"}
            />
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === "all"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
          >
            All ({tasks.length})
          </button>
          <button
            onClick={() => setFilter("active")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === "active"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
          >
            Active ({activeCount})
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === "completed"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
          >
            Completed ({completedCount})
          </button>
        </div>

        {/* Task List */}
        <TaskList
          tasks={tasks}
          loading={loading}
          error={error}
          onToggle={toggleTask}
          onDelete={deleteTask}
          onEdit={handleEdit}
        />
      </div>
    </div>
  );
}
