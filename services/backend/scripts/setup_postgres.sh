#!/bin/bash



# Wait for PostgreSQL to be healthy
until docker exec ics-postgres pg_isready -U ics_user > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL is ready!"

echo "🔄 Running database migrations..."
poetry run alembic upgrade head

echo "✅ Database setup complete!"
echo ""
echo "📊 Database Info:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: ics_threat_detection"
echo "  User: ics_user"
echo "  Password: ics_password"
echo ""
echo "🔗 Connection string:"
echo "  postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection"
