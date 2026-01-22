/**
 * Zustand store for application state management.
 * Replaces props drilling and provides centralized state.
 */
import { create } from 'zustand';
import type { Project, Tag, Task } from '../types';
import { projectApi, tagApi, taskApi } from '../services/api';
import { showSuccess, showError } from '../utils/toast';

interface AppState {
  // State
  projects: Project[];
  tags: Tag[];
  isLoadingProjects: boolean;
  isLoadingTags: boolean;
  
  // Actions
  loadProjects: () => Promise<void>;
  loadTags: () => Promise<void>;
  createProject: (data: { name: string; color?: string; description?: string }) => Promise<Project>;
  createTag: (data: { name: string; color?: string }) => Promise<Tag>;
  deleteProject: (id: number) => Promise<void>;
  deleteTag: (id: number) => Promise<void>;
  
  // Optimistic updates for tasks
  optimisticUpdateTask: (taskId: number, updates: Partial<Task>) => void;
  revertOptimisticUpdate: (taskId: number, originalTask: Task) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  projects: [],
  tags: [],
  isLoadingProjects: false,
  isLoadingTags: false,
  
  // Load projects
  loadProjects: async () => {
    set({ isLoadingProjects: true });
    try {
      const projects = await projectApi.getAll();
      set({ projects, isLoadingProjects: false });
    } catch (error) {
      console.error('Failed to load projects:', error);
      set({ isLoadingProjects: false });
      showError('Failed to load projects');
    }
  },
  
  // Load tags
  loadTags: async () => {
    set({ isLoadingTags: true });
    try {
      const tags = await tagApi.getAll();
      set({ tags, isLoadingTags: false });
    } catch (error) {
      console.error('Failed to load tags:', error);
      set({ isLoadingTags: false });
      showError('Failed to load tags');
    }
  },
  
  // Create project
  createProject: async (data) => {
    try {
      const newProject = await projectApi.create(data);
      set((state) => ({
        projects: [...state.projects, newProject]
      }));
      showSuccess(`Project "${newProject.name}" created`);
      return newProject;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create project';
      showError(message);
      throw error;
    }
  },
  
  // Create tag
  createTag: async (data) => {
    try {
      const newTag = await tagApi.create(data);
      set((state) => ({
        tags: [...state.tags, newTag]
      }));
      showSuccess(`Tag "${newTag.name}" created`);
      return newTag;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create tag';
      showError(message);
      throw error;
    }
  },
  
  // Delete project
  deleteProject: async (id: number) => {
    const project = get().projects.find(p => p.id === id);
    
    try {
      await projectApi.delete(id);
      set((state) => ({
        projects: state.projects.filter(p => p.id !== id)
      }));
      showSuccess(`Project "${project?.name || ''}" deleted`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete project';
      showError(message);
      throw error;
    }
  },
  
  // Delete tag
  deleteTag: async (id: number) => {
    const tag = get().tags.find(t => t.id === id);
    
    try {
      await tagApi.delete(id);
      set((state) => ({
        tags: state.tags.filter(t => t.id !== id)
      }));
      showSuccess(`Tag "${tag?.name || ''}" deleted`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete tag';
      showError(message);
      throw error;
    }
  },
  
  // Optimistic update (for instant UI feedback)
  optimisticUpdateTask: (taskId: number, updates: Partial<Task>) => {
    // This doesn't update the store directly, but can be used by components
    // Components will handle their own optimistic updates
  },
  
  // Revert optimistic update on error
  revertOptimisticUpdate: (taskId: number, originalTask: Task) => {
    // Components will handle reverting their own state
  }
}));
