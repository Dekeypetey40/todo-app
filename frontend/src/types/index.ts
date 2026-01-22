/**
 * TypeScript type definitions for the todo application.
 */

export type Priority = 'low' | 'medium' | 'high';
export type ViewType = 'all' | 'today' | 'week' | 'overdue';

export interface Project {
  id: number;
  name: string;
  color?: string;
  description?: string;
  created_at: string;
  task_count?: number;
}

export interface Tag {
  id: number;
  name: string;
  color?: string;
  created_at: string;
  task_count?: number;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  priority: Priority;
  due_date?: string; // YYYY-MM-DD format
  is_completed: boolean;
  project_id?: number;
  project?: Project;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export type ProjectCreate = Omit<Project, 'id' | 'created_at' | 'task_count'>;
export type ProjectUpdate = Partial<ProjectCreate>;

export type TagCreate = Omit<Tag, 'id' | 'created_at' | 'task_count'>;
export type TagUpdate = Partial<TagCreate>;

export type TaskCreate = Omit<Task, 'id' | 'created_at' | 'updated_at' | 'project' | 'tags'> & {
  tag_ids?: number[];
};
export type TaskUpdate = Partial<TaskCreate>;

export interface TaskFilters {
  completed?: boolean;
  project_id?: number;
  tag_ids?: number[];
  search?: string;
  view?: ViewType;
  sort?: string;
}

export interface ApiError {
  detail: string;
}

export interface AIParseRequest {
  text: string;
}

export interface AIParseResponse {
  title: string;
  description?: string;
  priority: Priority;
  due_date?: string;
  suggested_tags: string[];
}
