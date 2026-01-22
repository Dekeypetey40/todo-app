/**
 * Tests for TasksView component - verifies task creation functionality.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import TasksView from './TasksView';
import { taskApi } from '../services/api';
import type { Task } from '../types';

// Mock the API
vi.mock('../services/api', () => ({
  taskApi: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockProjects = [
  { id: 1, name: 'Work', color: '#3B82F6', task_count: 0, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockTags = [
  { id: 1, name: 'urgent', color: '#EF4444', task_count: 0, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockTasks: Task[] = [
  {
    id: 1,
    title: 'Existing Task',
    priority: 'medium',
    is_completed: false,
    tags: [],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  } as Task,
];

describe('TasksView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementations
    vi.mocked(taskApi.getAll).mockResolvedValue(mockTasks);
    vi.mocked(taskApi.create).mockResolvedValue({
      id: 2,
      title: 'New Task',
      priority: 'medium',
      is_completed: false,
      tags: [],
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    } as Task);
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <TasksView
          title="All Tasks"
          filters={{ view: 'all' }}
          projects={mockProjects}
          tags={mockTags}
          onTaskCreated={vi.fn()}
        />
      </BrowserRouter>
    );
  };

  it('renders task list', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Existing Task')).toBeInTheDocument();
    });
  });

  it('creates a task when form is submitted', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Existing Task')).toBeInTheDocument();
    });

    // Expand the task form
    const expandButton = screen.getByRole('button', { name: /add new task/i });
    await user.click(expandButton);

    // Fill in the form
    const titleInput = screen.getByPlaceholderText('What needs to be done?');
    await user.type(titleInput, 'New Task');

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    // Verify taskApi.create was called with correct data
    await waitFor(() => {
      expect(taskApi.create).toHaveBeenCalledWith({
        title: 'New Task',
        description: undefined,
        priority: 'medium',
        due_date: undefined,
        project_id: undefined,
        tag_ids: [],
        is_completed: false,
      });
    });

    // Verify tasks were reloaded
    expect(taskApi.getAll).toHaveBeenCalled();
  });

  it('creates a task with project and tags', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Existing Task')).toBeInTheDocument();
    });

    // Expand the task form
    const expandButton = screen.getByRole('button', { name: /add new task/i });
    await user.click(expandButton);

    // Fill in the form
    const titleInput = screen.getByPlaceholderText('What needs to be done?');
    await user.type(titleInput, 'Project Task');

    // Select a project
    const projectSelect = screen.getByLabelText('Project');
    await user.selectOptions(projectSelect, '1');

    // Select a tag
    const tagButton = screen.getByRole('button', { name: 'urgent' });
    await user.click(tagButton);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    // Verify taskApi.create was called with project and tags
    await waitFor(() => {
      expect(taskApi.create).toHaveBeenCalledWith({
        title: 'Project Task',
        description: undefined,
        priority: 'medium',
        due_date: undefined,
        project_id: 1,
        tag_ids: [1],
        is_completed: false,
      });
    });
  });

  it('displays error when task creation fails', async () => {
    const user = userEvent.setup();
    vi.mocked(taskApi.create).mockRejectedValue(new Error('Network error'));

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Existing Task')).toBeInTheDocument();
    });

    // Expand and submit
    const expandButton = screen.getByRole('button', { name: /add new task/i });
    await user.click(expandButton);

    const titleInput = screen.getByPlaceholderText('What needs to be done?');
    await user.type(titleInput, 'Failing Task');

    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    // Verify error is displayed
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('calls API and reloads tasks after successful task creation', async () => {
    const user = userEvent.setup();
    const mockOnTaskCreated = vi.fn();

    render(
      <BrowserRouter>
        <TasksView
          title="All Tasks"
          filters={{ view: 'all' }}
          projects={mockProjects}
          tags={mockTags}
          onTaskCreated={mockOnTaskCreated}
        />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Existing Task')).toBeInTheDocument();
    });

    // Expand the task form
    const expandButton = screen.getByRole('button', { name: /add new task/i });
    await user.click(expandButton);

    // Fill in the form
    const titleInput = screen.getByPlaceholderText('What needs to be done?');
    await user.type(titleInput, 'New Task');

    // Submit
    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    // Verify taskApi.create was called
    await waitFor(() => {
      expect(taskApi.create).toHaveBeenCalled();
    });

    // Verify tasks were reloaded (called at least twice: initial load + after create)
    await waitFor(() => {
      expect(taskApi.getAll).toHaveBeenCalledTimes(2);
    });

    // Verify parent callback was called
    expect(mockOnTaskCreated).toHaveBeenCalled();
  });
});
