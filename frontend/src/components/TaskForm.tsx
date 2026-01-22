/**
 * Collapsible TaskForm component for creating new tasks with AI parsing.
 * Uses Zustand store for projects and tags.
 */
import { useState, useEffect } from 'react';
import type { TaskCreate, Priority } from '../types';
import { aiApi } from '../services/api';
import { useAppStore } from '../store/appStore';

interface TaskFormProps {
  onSubmit: (task: TaskCreate) => Promise<void>;
}

export default function TaskForm({ onSubmit }: TaskFormProps) {
  // Get projects and tags from Zustand store
  const projects = useAppStore((state) => state.projects);
  const tags = useAppStore((state) => state.tags);
  const [isExpanded, setIsExpanded] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [dueDate, setDueDate] = useState('');
  const [projectId, setProjectId] = useState<number | undefined>();
  const [selectedTags, setSelectedTags] = useState<number[]>([]);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // AI parsing state
  const [useAI, setUseAI] = useState(false);
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [aiParsing, setAiParsing] = useState(false);
  const [suggestedTagNames, setSuggestedTagNames] = useState<string[]>([]);
  const [aiEnabled, setAiEnabled] = useState(false);

  // Check AI availability on mount
  useEffect(() => {
    const checkAI = async () => {
      try {
        const health = await aiApi.checkHealth();
        setAiEnabled(health.ai_enabled);
      } catch (err) {
        setAiEnabled(false);
      }
    };
    checkAI();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setIsSubmitting(true);

    try {
      const taskData: any = {
        title: title.trim(),
        priority,
        tag_ids: selectedTags,
        is_completed: false,
      };
      
      if (description.trim()) {
        taskData.description = description.trim();
      }
      if (dueDate) {
        taskData.due_date = dueDate;
      }
      if (projectId !== null && projectId !== undefined) {
        taskData.project_id = projectId;
      }
      
      await onSubmit(taskData);

      // Reset form and collapse
      resetForm();
      setIsExpanded(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleTag = (tagId: number) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const handleAIParse = async () => {
    if (!naturalLanguageInput.trim()) {
      setError('Please enter a task description');
      return;
    }

    setAiParsing(true);
    setError('');

    try {
      const parsed = await aiApi.parseTask(naturalLanguageInput);

      // Pre-fill form fields with AI suggestions
      setTitle(parsed.title);
      setDescription(parsed.description || '');
      setPriority(parsed.priority);
      setDueDate(parsed.due_date || '');

      // Store suggested tag names to show as options
      setSuggestedTagNames(parsed.suggested_tags);

      // Auto-select matching tags
      const matchingTagIds = tags
        .filter((tag) => parsed.suggested_tags.includes(tag.name.toLowerCase()))
        .map((tag) => tag.id);
      setSelectedTags(matchingTagIds);

      // Switch to manual mode so user can review/edit
      setUseAI(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse task with AI');
    } finally {
      setAiParsing(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setPriority('medium');
    setDueDate('');
    setProjectId(undefined);
    setSelectedTags([]);
    setNaturalLanguageInput('');
    setSuggestedTagNames([]);
    setError('');
    setUseAI(false);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 mb-6">
      {/* Header - Always Visible */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{isExpanded ? '−' : '+'}</span>
          <h2 className="text-lg font-semibold text-gray-800">Add New Task</h2>
          {aiEnabled && !isExpanded && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">AI Enabled</span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Form - Collapsible */}
      {isExpanded && (
        <form onSubmit={handleSubmit} className="px-6 pb-6 border-t border-gray-100">
          {/* AI Toggle Button */}
          {aiEnabled && (
            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={() => {
                  setUseAI(!useAI);
                  setError('');
                }}
                className="text-sm px-4 py-2 rounded-lg font-medium transition-all"
                style={{
                  backgroundColor: useAI ? '#3B82F6' : '#EFF6FF',
                  color: useAI ? 'white' : '#3B82F6',
                }}
              >
                {useAI ? '📝 Switch to Manual' : '✨ Use AI Parser'}
              </button>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {useAI ? (
            // AI Input Mode
            <div className="space-y-4 mt-4">
              <div>
                <label htmlFor="aiInput" className="block text-sm font-medium text-gray-700 mb-1">
                  Describe your task naturally
                </label>
                <textarea
                  id="aiInput"
                  value={naturalLanguageInput}
                  onChange={(e) => setNaturalLanguageInput(e.target.value)}
                  maxLength={500}
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                  placeholder='e.g., "Buy groceries tomorrow evening high priority" or "Schedule dentist appointment next Friday at 2pm"'
                  disabled={aiParsing}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Try including: what to do, when (due date), priority level, and any categories/tags
                </p>
              </div>

              <button
                type="button"
                onClick={handleAIParse}
                disabled={aiParsing || !naturalLanguageInput.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center"
              >
                {aiParsing ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Parsing with AI...
                  </>
                ) : (
                  '✨ Parse with AI'
                )}
              </button>
            </div>
          ) : (
            // Manual Input Mode
            <div className="space-y-4 mt-4">
              {/* Title */}
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  maxLength={200}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="What needs to be done?"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={2000}
                  rows={3}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                  placeholder="Add more details..."
                />
              </div>

              {/* Priority and Due Date */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as Priority)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    id="dueDate"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Project */}
              <div>
                <label htmlFor="project" className="block text-sm font-medium text-gray-700 mb-1">
                  Project
                </label>
                <select
                  id="project"
                  value={projectId || ''}
                  onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                >
                  <option value="">No Project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Tags */}
              {tags.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                    {suggestedTagNames.length > 0 && (
                      <span className="ml-2 text-xs text-blue-600 font-normal">
                        (AI suggested: {suggestedTagNames.join(', ')})
                      </span>
                    )}
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => (
                      <button
                        key={tag.id}
                        type="button"
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
                        {tag.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
              >
                {isSubmitting ? 'Adding...' : 'Add Task'}
              </button>
            </div>
          )}
        </form>
      )}
    </div>
  );
}
