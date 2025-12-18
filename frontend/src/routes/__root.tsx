import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createRootRoute, Link, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a query client
const queryClient = new QueryClient();

export const Route = createRootRoute({
	component: () => (
		<>
			<QueryClientProvider client={queryClient}>
				<div className="p-2 flex gap-2">
					<Link to="/" className="[&.active]:font-bold">
						Home
					</Link>{' '}
					<Link to="/about" className="[&.active]:font-bold">
						About
					</Link>
				</div>
				<hr />
				<Outlet />
				<ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-right" />
			</QueryClientProvider>
			<TanStackRouterDevtools initialIsOpen={false} />
		</>
	),
});
