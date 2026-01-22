import TasksView from '../components/TasksView';

interface OverdueViewProps {
  onTaskCreated: () => void;
}

export default function OverdueView({ onTaskCreated }: OverdueViewProps) {
  return (
    <TasksView
      title="Overdue Tasks"
      filters={{ view: 'overdue' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
