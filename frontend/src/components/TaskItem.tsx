/**
 * TaskItem component for displaying and editing individual tasks.
 */
import { useState } from 'react';
import type { Task, TaskUpdate, Priority } from '../types';
import { showDeleteConfirm, showError } from '../utils/toast.tsx';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: number, update: TaskUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [editPriority, setEditPriority] = useState(task.priority);
  const [editDueDate, setEditDueDate] = useState(task.due_date || '');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggleComplete = async () => {
    // Optimistic update - update UI immediately
    const previousState = task.is_completed;
    const optimisticTask = { ...task, is_completed: !previousState };
    
    // Update local state immediately for instant feedback
    Object.assign(task, optimisticTask);
    
    try {
      // Send update to server
      await onUpdate(task.id, { is_completed: !previousState });
    } catch (err) {
      // Revert on error
      task.is_completed = previousState;
      showError('Failed to update task');
      throw err;
    }
  };

  const handleSaveEdit = async () => {
    try {
      const updateData: any = {
        title: editTitle.trim(),
        priority: editPriority,
      };
      
      if (editDescription.trim()) {
        updateData.description = editDescription.trim();
      }
      if (editDueDate) {
        updateData.due_date = editDueDate;
      }
      
      await onUpdate(task.id, updateData);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update task:', err);
      showError('Failed to save changes');
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority);
    setEditDueDate(task.due_date || '');
    setIsEditing(false);
  };

  const handleDelete = () => {
    showDeleteConfirm('task', task.title, async () => {
      setIsDeleting(true);
      try {
        await onDelete(task.id);
      } catch (err) {
        console.error('Failed to delete task:', err);
        setIsDeleting(false);
        throw err;
      }
    });
  };

  const getPriorityColor = (priority: Priority) => {
    switch (priority) {
      case 'high':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && !task.is_completed;

  if (isEditing) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 mb-3 border-2 border-blue-500">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            placeholder="Task title"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            rows={2}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
            placeholder="Description"
          />
          <div className="grid grid-cols-2 gap-2">
            <select
              value={editPriority}
              onChange={(e) => setEditPriority(e.target.value as Priority)}
              className="border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <input
              type="date"
              value={editDueDate}
              onChange={(e) => setEditDueDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSaveEdit}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleCancelEdit}
              className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-4 mb-3 transition-all hover:border-gray-300 hover:shadow-sm ${
        isDeleting ? 'opacity-50' : ''
      } ${task.is_completed ? 'opacity-60' : ''}`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggleComplete}
          className="mt-1 h-5 w-5 text-indigo-600 rounded focus:ring-indigo-500 cursor-pointer"
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium ${
              task.is_completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p className="text-gray-600 mt-1 text-sm">{task.description}</p>
          )}

          {/* Tags, Project, Due Date */}
          <div className="flex flex-wrap gap-2 mt-2">
            {/* Priority Badge */}
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(
                task.priority
              )}`}
            >
              {task.priority}
            </span>

            {/* Project Badge */}
            {task.project && (
              <span
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200"
                style={task.project.color ? { backgroundColor: task.project.color + '15', borderColor: task.project.color + '40', color: task.project.color } : {}}
              >
                {task.project.name}
              </span>
            )}

            {/* Tags */}
            {task.tags.map((tag) => (
              <span
                key={tag.id}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-300"
                style={tag.color ? { backgroundColor: tag.color + '20', borderColor: tag.color } : {}}
              >
                #{tag.name}
              </span>
            ))}

            {/* Due Date */}
            {task.due_date && (
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  isOverdue
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-gray-50 text-gray-600 border-gray-200'
                } border`}
              >
                📅 {formatDate(task.due_date)}
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            className="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors"
            disabled={isDeleting}
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="text-gray-500 hover:text-rose-600 font-medium text-sm transition-colors"
            disabled={isDeleting}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
