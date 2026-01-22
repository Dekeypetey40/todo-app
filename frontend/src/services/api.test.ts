/**
 * Tests for API service - verifies API calls are made correctly.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { taskApi, projectApi, tagApi } from './api';
import type { TaskCreate, ProjectCreate, TagCreate } from '../types';

globalThis.fetch = vi.fn() as any;

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('taskApi', () => {
    it('creates a task with POST request', async () => {
      const mockTask: TaskCreate = {
        title: 'Test Task',
        description: 'Test Description',
        priority: 'high',
        due_date: '2024-12-31',
        project_id: 1,
        tag_ids: [1, 2],
        is_completed: false,
      };

      const mockResponse = {
        id: 1,
        ...mockTask,
        project: null,
        tags: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await taskApi.create(mockTask);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tasks',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockTask),
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it('fetches tasks with filters', async () => {
      const mockTasks = [
        {
          id: 1,
          title: 'Task 1',
          description: null,
          priority: 'medium',
          due_date: null,
          is_completed: false,
          project_id: null,
          project: null,
          tags: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockTasks,
      } as Response);

      const result = await taskApi.getAll({
        completed: false,
        project_id: 1,
        search: 'test',
        view: 'today',
      });

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tasks?completed=false&project_id=1&search=test&view=today'
      );

      expect(result).toEqual(mockTasks);
    });

    it('updates a task with PATCH request', async () => {
      const mockUpdate = { title: 'Updated Task' };
      const mockResponse = {
        id: 1,
        title: 'Updated Task',
        description: null,
        priority: 'medium',
        due_date: null,
        is_completed: false,
        project_id: null,
        project: null,
        tags: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await taskApi.update(1, mockUpdate);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tasks/1',
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockUpdate),
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it('deletes a task with DELETE request', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        status: 204,
        json: async () => ({}),
      } as Response);

      await taskApi.delete(1);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tasks/1',
        { method: 'DELETE' }
      );
    });

    it('throws error when API returns error', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        json: async () => ({ detail: 'Task not found' }),
      } as Response);

      await expect(taskApi.getById(999)).rejects.toThrow('Task not found');
    });
  });

  describe('projectApi', () => {
    it('creates a project', async () => {
      const mockProject: ProjectCreate = {
        name: 'New Project',
        color: '#3B82F6',
      };

      const mockResponse = {
        id: 1,
        ...mockProject,
        task_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await projectApi.create(mockProject);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockProject),
        }
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('tagApi', () => {
    it('creates a tag', async () => {
      const mockTag: TagCreate = {
        name: 'urgent',
        color: '#EF4444',
      };

      const mockResponse = {
        id: 1,
        ...mockTag,
        task_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await tagApi.create(mockTag);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tags',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockTag),
        }
      );

      expect(result).toEqual(mockResponse);
    });
  });
});
