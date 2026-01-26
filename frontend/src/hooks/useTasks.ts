/**
 * Task management hook with state management.
 *
 * Provides methods for fetching, creating, updating, and deleting tasks.
 * Handles loading states and error handling.
 */

"use client";

import { useState } from "react";
import { taskApi, type Task, ApiError } from "@/lib/api";

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: (filter?: { completed?: boolean }) => Promise<void>;
  createTask: (title: string, description?: string) => Promise<Task | null>;
  updateTask: (id: string, data: { title?: string; description?: string; completed?: boolean }) => Promise<Task | null>;
  toggleTask: (id: string) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
}

export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async (filter?: { completed?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await taskApi.list(filter);
      setTasks(response.tasks);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to fetch tasks";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (title: string, description?: string): Promise<Task | null> => {
    setError(null);
    try {
      const newTask = await taskApi.create({ title, description });
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to create task";
      setError(message);
      return null;
    }
  };

  const updateTask = async (
    id: string,
    data: { title?: string; description?: string; completed?: boolean }
  ): Promise<Task | null> => {
    setError(null);
    try {
      const updatedTask = await taskApi.update(id, data);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
      return updatedTask;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to update task";
      setError(message);
      return null;
    }
  };

  const toggleTask = async (id: string) => {
    setError(null);
    try {
      const updatedTask = await taskApi.toggle(id);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to toggle task";
      setError(message);
    }
  };

  const deleteTask = async (id: string) => {
    setError(null);
    try {
      await taskApi.delete(id);
      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to delete task";
      setError(message);
    }
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleTask,
    deleteTask,
  };
}
