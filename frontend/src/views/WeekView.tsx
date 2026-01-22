import TasksView from '../components/TasksView';

interface WeekViewProps {
  onTaskCreated: () => void;
}

export default function WeekView({ onTaskCreated }: WeekViewProps) {
  return (
    <TasksView
      title="This Week"
      filters={{ view: 'week' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
