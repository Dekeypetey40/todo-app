import TasksView from '../components/TasksView';

interface TodayViewProps {
  onTaskCreated: () => void;
}

export default function TodayView({ onTaskCreated }: TodayViewProps) {
  return (
    <TasksView
      title="Today"
      filters={{ view: 'today' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
