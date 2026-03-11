#!/bin/bash
set -e

COMMAND=$1

case "$COMMAND" in
    up)
        echo "Starting Supabase and Docker containers..."
        supabase start
        docker compose up -d api
        ;;
    down)
        echo "Stopping Supabase and Docker containers..."
        supabase stop
        docker compose down
        ;;
    migrate)
        echo "Running Alembic migrations inside the API container..."
        docker compose exec api uv run alembic upgrade head
        ;;
    makemigrations)
        MESSAGE=${2:-"auto_migration"}
        echo "Generating Alembic migration inside the API container..."
        docker compose exec api uv run alembic revision --autogenerate -m "$MESSAGE"
        ;;
    reset)
        if [ "$2" == "--api" ]; then
            echo "Resetting API container..."
            docker compose up -d --build api
        else
            echo "Resetting database..."
            supabase db reset
            echo "Running migrations..."
            docker compose exec api uv run alembic upgrade head
        fi
        ;;
    test)
        echo "Running tests with coverage..."
        uv run pytest --cov=app --cov-report=term-missing --cov-report=html
        ;;
    logs)
        echo "Showing API logs..."
        docker compose logs -f api
        ;;
    *)
        echo "Usage: $0 {up|down|logs|migrate|makemigrations <message>|reset [--api]|test}"
        exit 1
esac
