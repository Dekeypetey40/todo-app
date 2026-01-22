import TasksView from '../components/TasksView';

interface AllTasksViewProps {
  onTaskCreated: () => void;
}

export default function AllTasksView({ onTaskCreated }: AllTasksViewProps) {
  return (
    <TasksView
      title="All Tasks"
      filters={{ view: 'all' }}
      onTaskCreated={onTaskCreated}
    />
  );
}
