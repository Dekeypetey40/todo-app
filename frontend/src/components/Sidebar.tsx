/**
 * Sidebar component with navigation for projects and tags.
 */
import { Link, useLocation } from 'react-router-dom';
import type { Project, Tag } from '../types';

interface SidebarProps {
  projects: Project[];
  tags: Tag[];
  onCreateProject: () => void;
  onCreateTag: () => void;
}

export default function Sidebar({ projects, tags, onCreateProject, onCreateTag }: SidebarProps) {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-200">
        <Link to="/" className="text-xl font-semibold text-gray-800 hover:text-gray-600 transition-colors">
          📝 Todo App
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Smart Views */}
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Views
          </h3>
          <div className="space-y-1">
            <Link
              to="/"
              className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">📋</span>
              All Tasks
            </Link>
            <Link
              to="/today"
              className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/today')
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">☀️</span>
              Today
            </Link>
            <Link
              to="/week"
              className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/week')
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">📅</span>
              This Week
            </Link>
            <Link
              to="/overdue"
              className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/overdue')
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">⚠️</span>
              Overdue
            </Link>
          </div>
        </div>

        {/* Projects */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Projects
            </h3>
            <button
              onClick={onCreateProject}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Add project"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          {projects.length === 0 ? (
            <p className="text-sm text-gray-400 px-3 py-2">No projects yet</p>
          ) : (
            <div className="space-y-1">
              {projects.map((project) => (
                <Link
                  key={project.id}
                  to={`/project/${project.id}`}
                  className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(`/project/${project.id}`)
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center">
                    <div
                      className="w-2 h-2 rounded-full mr-2"
                      style={{ backgroundColor: project.color }}
                    />
                    <span className="flex-1 truncate">{project.name}</span>
                    <span className="text-xs text-gray-400 ml-2">
                      {project.task_count || 0}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Tags */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Tags
            </h3>
            <button
              onClick={onCreateTag}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Add tag"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          {tags.length === 0 ? (
            <p className="text-sm text-gray-400 px-3 py-2">No tags yet</p>
          ) : (
            <div className="flex flex-wrap gap-2 px-3">
              {tags.map((tag) => (
                <Link
                  key={tag.id}
                  to={`/tag/${tag.id}`}
                  className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
                  style={{
                    backgroundColor: tag.color ? `${tag.color}15` : undefined,
                    color: tag.color || undefined,
                  }}
                >
                  #{tag.name}
                </Link>
              ))}
            </div>
          )}
        </div>
      </nav>
    </aside>
  );
}
