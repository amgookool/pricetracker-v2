import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/password-reset/')({
	component: () => <div className="p-2">Hello from Password Reset!</div>,
});
