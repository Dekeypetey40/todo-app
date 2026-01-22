/**
 * API client for interacting with the backend.
 */
import DOMPurify from 'dompurify';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskFilters,
  Project,
  ProjectCreate,
  ProjectUpdate,
  Tag,
  TagCreate,
  TagUpdate,
  ApiError,
  AIParseRequest,
  AIParseResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Sanitize user input to prevent XSS attacks.
 */
function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
}

/**
 * Paginated response type.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/**
 * Handle API errors consistently with better error messages.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }

  // Try to parse JSON, but handle parsing errors gracefully
  let data;
  try {
    data = await response.json();
  } catch (e) {
    // If JSON parsing fails, provide a better error message
    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }
    throw new Error('Invalid response from server');
  }

  if (!response.ok) {
    const error: ApiError = data;
    // Provide more context in error messages
    const errorMessage = error.detail || `Request failed: ${response.status} ${response.statusText}`;
    
    // Log the error for debugging
    console.error('API Error:', {
      status: response.status,
      statusText: response.statusText,
      url: response.url,
      detail: error.detail
    });
    
    throw new Error(errorMessage);
  }

  return data;
}

/**
 * Build query string from filters object.
 */
function buildQueryString(filters: TaskFilters): string {
  const params = new URLSearchParams();

  if (filters.completed !== undefined) {
    params.append('completed', String(filters.completed));
  }
  if (filters.project_id !== undefined) {
    params.append('project_id', String(filters.project_id));
  }
  if (filters.tag_ids && filters.tag_ids.length > 0) {
    filters.tag_ids.forEach((id) => params.append('tag_ids', String(id)));
  }
  if (filters.search) {
    params.append('search', filters.search);
  }
  if (filters.view) {
    params.append('view', filters.view);
  }
  if (filters.sort) {
    params.append('sort', filters.sort);
  }

  return params.toString();
}

// Task API
export const taskApi = {
  async getAll(filters: TaskFilters = {}, page: number = 1, pageSize: number = 50): Promise<PaginatedResponse<Task>> {
    const params = new URLSearchParams(buildQueryString(filters));
    params.append('page', String(page));
    params.append('page_size', String(pageSize));
    
    const url = `${API_BASE_URL}/api/tasks?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse<PaginatedResponse<Task>>(response);
  },

  async getById(id: number): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`);
    return handleResponse<Task>(response);
  },

  async create(task: TaskCreate): Promise<Task> {
    // Sanitize inputs
    const sanitizedTask = {
      ...task,
      title: sanitizeInput(task.title),
      description: task.description ? sanitizeInput(task.description) : undefined,
    };
    
    const response = await fetch(`${API_BASE_URL}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedTask),
    });
    return handleResponse<Task>(response);
  },

  async update(id: number, task: TaskUpdate): Promise<Task> {
    // Sanitize inputs if provided
    const sanitizedTask = { ...task };
    if (task.title) {
      sanitizedTask.title = sanitizeInput(task.title);
    }
    if (task.description) {
      sanitizedTask.description = sanitizeInput(task.description);
    }
    
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedTask),
    });
    return handleResponse<Task>(response);
  },

  async delete(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  },
};

// Project API
export const projectApi = {
  async getAll(): Promise<Project[]> {
    const response = await fetch(`${API_BASE_URL}/api/projects`);
    return handleResponse<Project[]>(response);
  },

  async getById(id: number): Promise<Project> {
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`);
    return handleResponse<Project>(response);
  },

  async create(project: ProjectCreate): Promise<Project> {
    // Sanitize inputs
    const sanitizedProject = {
      ...project,
      name: sanitizeInput(project.name),
      description: project.description ? sanitizeInput(project.description) : undefined,
    };
    
    const response = await fetch(`${API_BASE_URL}/api/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedProject),
    });
    return handleResponse<Project>(response);
  },

  async update(id: number, project: ProjectUpdate): Promise<Project> {
    // Sanitize inputs if provided
    const sanitizedProject = { ...project };
    if (project.name) {
      sanitizedProject.name = sanitizeInput(project.name);
    }
    if (project.description) {
      sanitizedProject.description = sanitizeInput(project.description);
    }
    
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedProject),
    });
    return handleResponse<Project>(response);
  },

  async delete(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  },

  async getTasks(id: number): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}/tasks`);
    return handleResponse<Task[]>(response);
  },
};

// Tag API
export const tagApi = {
  async getAll(): Promise<Tag[]> {
    const response = await fetch(`${API_BASE_URL}/api/tags`);
    return handleResponse<Tag[]>(response);
  },

  async getById(id: number): Promise<Tag> {
    const response = await fetch(`${API_BASE_URL}/api/tags/${id}`);
    return handleResponse<Tag>(response);
  },

  async create(tag: TagCreate): Promise<Tag> {
    // Sanitize inputs
    const sanitizedTag = {
      ...tag,
      name: sanitizeInput(tag.name),
    };
    
    const response = await fetch(`${API_BASE_URL}/api/tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedTag),
    });
    return handleResponse<Tag>(response);
  },

  async update(id: number, tag: TagUpdate): Promise<Tag> {
    // Sanitize inputs if provided
    const sanitizedTag = { ...tag };
    if (tag.name) {
      sanitizedTag.name = sanitizeInput(tag.name);
    }
    
    const response = await fetch(`${API_BASE_URL}/api/tags/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedTag),
    });
    return handleResponse<Tag>(response);
  },

  async delete(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/tags/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  },

  async getTasks(id: number): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/tags/${id}/tasks`);
    return handleResponse<Task[]>(response);
  },
};

// AI API
export const aiApi = {
  async parseTask(text: string): Promise<AIParseResponse> {
    const response = await fetch(`${API_BASE_URL}/api/ai/parse-task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text } as AIParseRequest),
    });
    return handleResponse<AIParseResponse>(response);
  },

  async checkHealth(): Promise<{ ai_enabled: boolean; model: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/ai/health`);
    return handleResponse<{ ai_enabled: boolean; model: string; message: string }>(response);
  },
};
