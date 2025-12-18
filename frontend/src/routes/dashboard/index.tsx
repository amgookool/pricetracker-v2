import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/dashboard/')({
    component: ()=> (
        <div className='p-2'>Hello from Dashboard!</div>
    ),
});


