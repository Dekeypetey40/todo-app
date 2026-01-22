/**
 * TaskList component for displaying and filtering tasks.
 */
import { useState, useEffect } from 'react';
import type { Task, TaskUpdate, TaskFilters, Project, Tag, ViewType } from '../types';
import { taskApi } from '../services/api';
import TaskItem from './TaskItem';

interface TaskListProps {
  projects: Project[];
  tags: Tag[];
  refreshTrigger?: number;
}

export default function TaskList({ projects, tags, refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [selectedView, setSelectedView] = useState<ViewType>('all');
  const [selectedProject, setSelectedProject] = useState<number | undefined>();
  const [selectedTags, setSelectedTags] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [completedFilter, setCompletedFilter] = useState<boolean | undefined>();
  const [sortBy, setSortBy] = useState('created_at_desc');

  const loadTasks = async () => {
    setLoading(true);
    setError('');

    try {
      const filters: TaskFilters = {
        view: selectedView,
        sort: sortBy,
      };
      
      if (selectedProject !== null && selectedProject !== undefined) {
        filters.project_id = selectedProject;
      }
      if (selectedTags.length > 0) {
        filters.tag_ids = selectedTags;
      }
      if (searchQuery) {
        filters.search = searchQuery;
      }
      if (completedFilter !== undefined) {
        filters.completed = completedFilter;
      }

      const fetchedTasks = await taskApi.getAll(filters);
      setTasks(fetchedTasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [selectedView, selectedProject, selectedTags, searchQuery, completedFilter, sortBy, refreshTrigger]);

  const handleUpdateTask = async (id: number, update: TaskUpdate) => {
    try {
      await taskApi.update(id, update);
      await loadTasks();
    } catch (err) {
      console.error('Failed to update task:', err);
      throw err;
    }
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await taskApi.delete(id);
      await loadTasks();
    } catch (err) {
      console.error('Failed to delete task:', err);
      throw err;
    }
  };

  const toggleTag = (tagId: number) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const clearFilters = () => {
    setSelectedView('all');
    setSelectedProject(undefined);
    setSelectedTags([]);
    setSearchQuery('');
    setCompletedFilter(undefined);
    setSortBy('created_at_desc');
  };

  const hasActiveFilters = selectedView !== 'all' || selectedProject || selectedTags.length > 0 || searchQuery || completedFilter !== undefined;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading tasks...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Filters Section */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="space-y-4">
          {/* Smart Views */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">View</label>
            <div className="flex flex-wrap gap-2">
              {(['all', 'today', 'week', 'overdue'] as ViewType[]).map((view) => (
                <button
                  key={view}
                  onClick={() => setSelectedView(view)}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    selectedView === view
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {view.charAt(0).toUpperCase() + view.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Search */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              id="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tasks..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          {/* Project Filter */}
          <div>
            <label htmlFor="projectFilter" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Project
            </label>
            <select
              id="projectFilter"
              value={selectedProject || ''}
              onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">All Projects</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {/* Tag Filter */}
          {tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Tags</label>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    onClick={() => toggleTag(tag.id)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      selectedTags.includes(tag.id)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                    style={
                      selectedTags.includes(tag.id) && tag.color
                        ? { backgroundColor: tag.color }
                        : {}
                    }
                  >
                    #{tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Completion Filter and Sort */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="completedFilter" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="completedFilter"
                value={completedFilter === undefined ? '' : String(completedFilter)}
                onChange={(e) =>
                  setCompletedFilter(e.target.value === '' ? undefined : e.target.value === 'true')
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Tasks</option>
                <option value="false">Active</option>
                <option value="true">Completed</option>
              </select>
            </div>

            <div>
              <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                id="sortBy"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="created_at_desc">Newest First</option>
                <option value="created_at_asc">Oldest First</option>
                <option value="due_date_asc">Due Date (Soonest)</option>
                <option value="due_date_desc">Due Date (Latest)</option>
                <option value="priority">Priority</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear all filters
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Tasks List */}
      {tasks.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No tasks found</h3>
          <p className="text-gray-500">
            {hasActiveFilters
              ? 'Try adjusting your filters or create a new task.'
              : 'Create your first task to get started!'}
          </p>
        </div>
      ) : (
        <div>
          <div className="mb-3 text-sm text-gray-600">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
          </div>
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={handleUpdateTask}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      )}
    </div>
  );
}
