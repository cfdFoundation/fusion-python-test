#!/bin/bash

case "$1" in
    build)
        echo "Building Docker image..."
        docker-compose build --no-cache
        ;;
    up)
        echo "Starting application..."
        docker-compose up
        ;;
    start)
        echo "Starting application in background..."
        docker-compose up -d web
        echo "Application running at http://localhost:5000/graphql"
        ;;
    stop)
        echo "Stopping application..."
        docker-compose down
        ;;
    test)
        echo "Running tests..."
        docker-compose down
        docker-compose up -d web
        sleep 5
        docker-compose run --rm test
        ;;
    test-verbose)
        echo "Running tests with verbose output - showing requests/responses..."
        docker-compose down
        docker-compose up -d web
        sleep 5
        docker-compose run --rm -e VERBOSE=1 test
        ;;
    test-debug)
        echo "Running tests with full debug output..."
        docker-compose down
        docker-compose up -d web
        echo
        echo "Waiting for server to start..."
        sleep 5
        echo
        echo "=== STARTING TESTS WITH FULL DEBUG OUTPUT ==="
        echo
        docker-compose run --rm -e VERBOSE=1 test
        echo
        echo "=== CHECKING SERVER LOGS ==="
        docker-compose logs web --tail=50
        ;;
    shell)
        echo "Opening shell in container..."
        docker-compose run --rm web /bin/bash
        ;;
    init-db)
        echo "Initializing database with sample data..."
        docker-compose run --rm web python init_db.py
        ;;
    logs)
        docker-compose logs -f web
        ;;
    clean)
        echo "Cleaning up everything..."
        docker-compose down -v
        docker network prune -f
        docker system prune -af
        ;;
    fresh)
        echo "Complete fresh start..."
        docker-compose down -v
        docker network prune -f
        docker-compose build --no-cache
        docker-compose up
        ;;
    restart)
        echo "Restarting everything..."
        docker-compose down
        docker network prune -f
        docker-compose up
        ;;
    graphql)
        echo "Opening GraphQL playground in browser..."
        # Detect OS and use appropriate command
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open http://localhost:5000/graphql
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            open http://localhost:5000/graphql
        else
            echo "Please open http://localhost:5000/graphql in your browser"
        fi
        ;;
    demo)
        echo "Running demo with verbose output..."
        echo
        echo "=== STARTING APPLICATION ==="
        docker-compose up -d web
        sleep 5
        echo
        echo "=== RUNNING TESTS WITH REQUESTS/RESPONSES ==="
        docker-compose run --rm -e VERBOSE=1 test
        echo
        echo "GraphQL Playground: http://localhost:5000/graphql"
        echo "To stop: ./docker.sh stop"
        ;;
    *)
        echo "Usage: ./docker.sh [command]"
        echo
        echo "Main Commands:"
        echo "  up              - Start the application in foreground"
        echo "  start           - Start the application in background"
        echo "  stop            - Stop the application"
        echo "  test            - Run tests with normal output"
        echo "  test-verbose    - Run tests showing requests/responses"
        echo "  test-debug      - Run tests with full debug + server logs"
        echo "  graphql         - Open GraphQL playground in browser"
        echo
        echo "Maintenance Commands:"
        echo "  build           - Build Docker image"
        echo "  shell           - Open shell in container"
        echo "  init-db         - Add sample data"
        echo "  logs            - View application logs"
        echo "  clean           - Remove everything"
        echo "  fresh           - Clean rebuild and start"
        echo "  restart         - Stop and restart cleanly"
        echo
        echo "Special Commands:"
        echo "  demo            - Run full demo with verbose output"
        echo
        echo "Quick start:"
        echo "  ./docker.sh start      - start app"
        echo "  ./docker.sh test       - run tests"
        echo "  ./docker.sh graphql    - open playground"
        echo
        echo "For debugging:"
        echo "  ./docker.sh test-verbose   - see all requests/responses"
        echo "  ./docker.sh test-debug     - full debug with server logs"
        ;;
esac
