import { useParams } from 'react-router-dom';
import TasksView from '../components/TasksView';
import { useAppStore } from '../store/appStore';

interface TagViewProps {
  onTaskCreated: () => void;
}

export default function TagView({ onTaskCreated }: TagViewProps) {
  const { id } = useParams<{ id: string }>();
  const tagId = id ? parseInt(id) : undefined;
  const tags = useAppStore((state) => state.tags);
  const tag = tags.find((t) => t.id === tagId);

  if (!tag) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">Tag not found</h3>
          <p className="text-gray-500">The tag you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <TasksView
      title={`#${tag.name}`}
      filters={{ tag_ids: [tagId!], view: 'all' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
