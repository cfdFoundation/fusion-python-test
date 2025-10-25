@echo off

if "%1"=="build" (
    echo Building Docker image...
    docker-compose build --no-cache
) else if "%1"=="up" (
    echo Starting application...
    docker-compose up
) else if "%1"=="start" (
    echo Starting application in background...
    docker-compose up -d web
    echo Application running at http://localhost:5000/graphql
) else if "%1"=="stop" (
    echo Stopping application...
    docker-compose down
) else if "%1"=="test" (
    echo Running tests...
    docker-compose down
    docker-compose up -d web
    timeout /t 5 >nul
    docker-compose run --rm test
) else if "%1"=="test-verbose" (
    echo Running tests with verbose output - showing requests/responses...
    docker-compose down
    docker-compose up -d web
    timeout /t 5 >nul
    docker-compose run --rm -e VERBOSE=1 test
) else if "%1"=="test-debug" (
    echo Running tests with full debug output...
    docker-compose down
    docker-compose up -d web
    echo.
    echo Waiting for server to start...
    timeout /t 5 >nul
    echo.
    echo === STARTING TESTS WITH FULL DEBUG OUTPUT ===
    echo.
    docker-compose run --rm -e VERBOSE=1 test
    echo.
    echo === CHECKING SERVER LOGS ===
    docker-compose logs web --tail=50
) else if "%1"=="shell" (
    echo Opening shell in container...
    docker-compose run --rm web /bin/bash
) else if "%1"=="init-db" (
    echo Initializing database with sample data...
    docker-compose run --rm web python init_db.py
) else if "%1"=="logs" (
    docker-compose logs -f web
) else if "%1"=="clean" (
    echo Cleaning up everything...
    docker-compose down -v
    docker network prune -f
    docker system prune -af
) else if "%1"=="fresh" (
    echo Complete fresh start...
    docker-compose down -v
    docker network prune -f
    docker-compose build --no-cache
    docker-compose up
) else if "%1"=="restart" (
    echo Restarting everything...
    docker-compose down
    docker network prune -f
    docker-compose up
) else if "%1"=="graphql" (
    echo Opening GraphQL playground in browser...
    start http://localhost:5000/graphql
) else if "%1"=="demo" (
    echo Running demo with verbose output...
    echo.
    echo === STARTING APPLICATION ===
    docker-compose up -d web
    timeout /t 5 >nul
    echo.
    echo === RUNNING TESTS WITH REQUESTS/RESPONSES ===
    docker-compose run --rm -e VERBOSE=1 test
    echo.
    echo GraphQL Playground: http://localhost:5000/graphql
    echo To stop: docker.bat stop
) else (
    echo Usage: docker.bat [command]
    echo.
    echo Main Commands:
    echo   up              - Start the application in foreground
    echo   start           - Start the application in background
    echo   stop            - Stop the application
    echo   test            - Run tests with normal output
    echo   test-verbose    - Run tests showing requests/responses
    echo   test-debug      - Run tests with full debug + server logs
    echo   graphql         - Open GraphQL playground in browser
    echo.
    echo Maintenance Commands:
    echo   build           - Build Docker image
    echo   shell           - Open shell in container
    echo   init-db         - Add sample data
    echo   logs            - View application logs
    echo   clean           - Remove everything
    echo   fresh           - Clean rebuild and start
    echo   restart         - Stop and restart cleanly
    echo.
    echo Special Commands:
    echo   demo            - Run full demo with verbose output
    echo.
    echo Quick start:
    echo   docker.bat start      - start app
    echo   docker.bat test       - run tests
    echo   docker.bat graphql    - open playground
    echo.
    echo For debugging:
    echo   docker.bat test-verbose   - see all requests/responses
    echo   docker.bat test-debug     - full debug with server logs
)
