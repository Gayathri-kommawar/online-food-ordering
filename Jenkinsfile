pipeline {
    agent any

    stages {

        stage('Pull') {
            steps {
                echo 'Pulling project from GitHub'

                git branch: 'main',
                    url: 'https://github.com/Gayathri-kommawar/online-food-ordering.git'
            }
        }

        stage('Prepare Environment') {
            steps {
                echo 'Creating environment configuration'

                bat 'copy /Y .env.example .env'
            }
        }

        stage('Build') {
            steps {
                echo 'Building Order API Docker image'

                bat 'docker compose build order-api'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Starting complete application'

                bat 'docker compose up -d'
            }
        }

        stage('Wait for Services') {
            steps {
                echo 'Waiting for application to become ready'

                bat '''
                for /L %%i in (1,1,30) do (
                    curl.exe -fsS http://localhost:8080/health > health.txt
                    if not errorlevel 1 exit /b 0
                    timeout /t 2 /nobreak >nul
                )

                echo Application did not become healthy
                exit /b 1
                '''
            }
        }

        stage('Create Test Order') {
            steps {
                echo 'Creating test food order'

                bat '''
                curl.exe -fsS -X POST http://localhost:8080/orders ^
                -H "Content-Type: application/json" ^
                -d "{\\"customer_name\\":\\"Jenkins Test\\",\\"food_item\\":\\"Burger\\",\\"quantity\\":2}" ^
                > order-response.json

                type order-response.json
                '''
            }
        }

        stage('Retrieve Order') {
            steps {
                echo 'Retrieving existing orders'

                bat '''
                curl.exe -fsS http://localhost:8080/orders > orders.json
                type orders.json
                '''
            }
        }

        stage('Verify Database') {
            steps {
                echo 'Verifying order in PostgreSQL'

                bat '''
                docker exec food-order-db psql -U orderuser -d ordersdb -tAc "SELECT COUNT(*) FROM orders WHERE customer_name='Jenkins Test';" > db-count.txt

                set /p DB_COUNT=<db-count.txt

                echo Database matching orders: %DB_COUNT%

                if "%DB_COUNT%"=="0" (
                    echo Order was not found in PostgreSQL
                    exit /b 1
                )
                '''
            }
        }
    }

    post {

        failure {
            echo 'Deployment or verification failed. Displaying logs.'

            bat '''
            docker compose ps -a
            docker compose logs --tail=100 nginx
            docker compose logs --tail=100 order-api
            docker compose logs --tail=100 db
            '''
        }

        always {
            echo 'Stopping application containers while preserving PostgreSQL volume'

            bat 'docker compose down'
        }
    }
}