--@block Select all users from the `users` table
SELECT * FROM users;

--@block select all user agents from the `user_agents` table
SELECT * FROM user_agents;

--@block select all proxies from the `proxies` table
SELECT * FROM proxies WHERE proxy_type = 'HTTP';