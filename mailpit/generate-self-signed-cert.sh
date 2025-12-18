#!/usr/bin/env bash
# Generate a self-signed TLS certificate and key for Mailpit STARTTLS
# The cert/key will be placed in ./mailpit/certs/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/certs"

# Create certs directory if it doesn't exist
mkdir -p "$CERTS_DIR"

echo "Generating self-signed certificate and key..."

# Generate self-signed certificate valid for 365 days
openssl req -x509 -newkey rsa:4096 -nodes -sha256 -days 365 \
  -subj "/C=US/ST=State/L=City/O=PriceTracker/OU=Development/CN=localhost" \
  -keyout "$CERTS_DIR/key.pem" \
  -out "$CERTS_DIR/cert.pem"

echo "✓ Certificate generated successfully!"
echo "  Certificate: $CERTS_DIR/cert.pem"
echo "  Private Key: $CERTS_DIR/key.pem"
echo ""
echo "You can now start Mailpit with STARTTLS enabled:"
echo "  docker compose up -d mailpit"
