import { useParams } from 'react-router-dom';
import TasksView from '../components/TasksView';
import { useAppStore } from '../store/appStore';

interface ProjectViewProps {
  onTaskCreated: () => void;
}

export default function ProjectView({ onTaskCreated }: ProjectViewProps) {
  const { id } = useParams<{ id: string }>();
  const projectId = id ? parseInt(id) : undefined;
  const projects = useAppStore((state) => state.projects);
  const project = projects.find((p) => p.id === projectId);

  if (!project) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">Project not found</h3>
          <p className="text-gray-500">The project you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <TasksView
      title={project.name}
      filters={{ project_id: project.id, view: 'all' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
