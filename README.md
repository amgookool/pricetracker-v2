# Price Pulse

Price Pulse is a comprehensive price tracking application designed to help users monitor and manage product prices across various e-commerce platforms. With features like user authentication, price alerts, and detailed analytics, Price Pulse empowers users to make informed purchasing decisions and save money.

## Development Setup

To set up the development environment for Price Pulse, follow these steps:

1. Create `.env` file based on the provided `.env.example`:

   ```bash
   cp .env.example .env
   ```

    Edit the `.env` file to configure your environment variables as needed.

2. Symbolically create a relative link to both frontend and backend directories:

   ```bash
   ln -sr ../frontend frontend
   ln -sr ../backend backend
   ```
