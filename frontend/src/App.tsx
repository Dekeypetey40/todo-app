/**
 * Main App component with routing and layout.
 * Uses Zustand for centralized state management.
 */
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useAppStore } from './store/appStore';
import Sidebar from './components/Sidebar';
import AllTasksView from './views/AllTasksView';
import TodayView from './views/TodayView';
import WeekView from './views/WeekView';
import OverdueView from './views/OverdueView';
import ProjectView from './views/ProjectView';
import TagView from './views/TagView';

export default function App() {
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showTagModal, setShowTagModal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Get state and actions from Zustand store
  const { projects, tags, loadProjects, loadTags, createProject, createTag } = useAppStore();

  // Load projects and tags on mount and when refreshKey changes
  useEffect(() => {
    loadProjects();
    loadTags();
  }, [refreshKey, loadProjects, loadTags]);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleCreateProject = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = formData.get('name') as string;
    const color = formData.get('color') as string;

    if (!name.trim()) return;

    try {
      await createProject({ name: name.trim(), color: color || '#6366F1' });
      setShowProjectModal(false);
      e.currentTarget.reset();
    } catch (err) {
      // Error already handled by store
    }
  };

  const handleCreateTag = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = formData.get('name') as string;
    const color = formData.get('color') as string;

    if (!name.trim()) return;

    try {
      await createTag({ name: name.trim(), color: color || '#6B7280' });
      setShowTagModal(false);
      e.currentTarget.reset();
    } catch (err) {
      // Error already handled by store
    }
  };

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar
          projects={projects}
          tags={tags}
          onCreateProject={() => setShowProjectModal(true)}
          onCreateTag={() => setShowTagModal(true)}
        />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-8">
            <Routes>
              <Route
                path="/"
                element={<AllTasksView onTaskCreated={handleRefresh} />}
              />
              <Route
                path="/today"
                element={<TodayView onTaskCreated={handleRefresh} />}
              />
              <Route
                path="/week"
                element={<WeekView onTaskCreated={handleRefresh} />}
              />
              <Route
                path="/overdue"
                element={<OverdueView onTaskCreated={handleRefresh} />}
              />
              <Route
                path="/project/:id"
                element={<ProjectView onTaskCreated={handleRefresh} />}
              />
              <Route
                path="/tag/:id"
                element={<TagView onTaskCreated={handleRefresh} />}
              />
            </Routes>
          </div>
        </main>

        {/* Project Modal */}
        {showProjectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">Create Project</h2>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    placeholder="Project name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Color
                  </label>
                  <input
                    type="color"
                    name="color"
                    defaultValue="#6366F1"
                    className="w-full h-10 border border-gray-300 rounded-lg cursor-pointer"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg transition-colors"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowProjectModal(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Tag Modal */}
        {showTagModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">Create Tag</h2>
              <form onSubmit={handleCreateTag} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    placeholder="Tag name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Color
                  </label>
                  <input
                    type="color"
                    name="color"
                    defaultValue="#6B7280"
                    className="w-full h-10 border border-gray-300 rounded-lg cursor-pointer"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg transition-colors"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowTagModal(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </BrowserRouter>
  );
}
