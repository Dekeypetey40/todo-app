/**
 * Shared TasksView component with pagination and filtering.
 * Uses Zustand store for projects and tags.
 */
import { useState, useEffect } from 'react';
import type { Task, TaskCreate, TaskUpdate, TaskFilters } from '../types';
import { taskApi } from '../services/api';
import { showSuccess, showError } from '../utils/toast.tsx';
import { useAppStore } from '../store/appStore';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';

interface TasksViewProps {
  title: string;
  filters: TaskFilters;
  onTaskCreated: () => void;
}

const TASKS_PER_PAGE = 50;

export default function TasksView({ title, filters, onTaskCreated }: TasksViewProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTasks, setTotalTasks] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('created_at_desc');

  const loadTasks = async (page: number = 1) => {
    setLoading(true);
    setError('');

    try {
      const allFilters: TaskFilters = {
        ...filters,
        sort: sortBy,
      };
      
      if (searchQuery) {
        allFilters.search = searchQuery;
      }

      const response = await taskApi.getAll(allFilters, page, TASKS_PER_PAGE);
      setTasks(response.items);
      setTotalPages(response.pages);
      setTotalTasks(response.total);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks(1); // Reset to page 1 when filters change
  }, [filters, searchQuery, sortBy]);

  const handleUpdateTask = async (id: number, update: TaskUpdate) => {
    try {
      await taskApi.update(id, update);
      await loadTasks();
      onTaskCreated(); // Refresh sidebar counts
    } catch (err) {
      console.error('Failed to update task:', err);
      throw err;
    }
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await taskApi.delete(id);
      await loadTasks();
      onTaskCreated(); // Refresh sidebar counts
    } catch (err) {
      console.error('Failed to delete task:', err);
      throw err;
    }
  };

  const handleTaskCreated = async (task: TaskCreate) => {
    try {
      await taskApi.create(task);
      await loadTasks();
      onTaskCreated();
      showSuccess('Task created successfully');
    } catch (err) {
      showError('Failed to create task. Please try again.');
      throw err;
    }
  };

  // Pagination is now handled server-side
  const startIndex = (currentPage - 1) * TASKS_PER_PAGE;
  const endIndex = Math.min(startIndex + TASKS_PER_PAGE, totalTasks);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-600">
          {totalTasks} {totalTasks === 1 ? 'task' : 'tasks'}
        </p>
      </div>

      {/* Task Form */}
      <TaskForm onSubmit={handleTaskCreated} />

      {/* Search and Sort */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none bg-white"
        >
          <option value="created_at_desc">Newest First</option>
          <option value="created_at_asc">Oldest First</option>
          <option value="due_date_asc">Due Date (Soonest)</option>
          <option value="due_date_desc">Due Date (Latest)</option>
          <option value="priority">Priority</option>
          <option value="title">Title (A-Z)</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Tasks List */}
      {totalTasks === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No tasks found</h3>
          <p className="text-gray-500">
            {searchQuery
              ? 'Try adjusting your search or create a new task.'
              : 'Create your first task to get started!'}
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {startIndex + 1}-{endIndex} of {totalTasks}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => loadTasks(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    let page;
                    if (totalPages <= 5) {
                      page = i + 1;
                    } else if (currentPage <= 3) {
                      page = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      page = totalPages - 4 + i;
                    } else {
                      page = currentPage - 2 + i;
                    }
                    return (
                      <button
                        key={page}
                        onClick={() => loadTasks(page)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentPage === page
                            ? 'bg-indigo-600 text-white'
                            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => loadTasks(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
