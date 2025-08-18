# Messaging App CI/CD Setup

This repository contains the configuration files for setting up CI/CD pipelines using Jenkins and GitHub Actions for the Django messaging application.

## Jenkins Setup

### 1. Install Jenkins in Docker

Run the following command to install Jenkins in a Docker container:

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

### 2. Access Jenkins Dashboard

Visit http://localhost:8080 in your browser and follow the instructions to set up and configure Jenkins.

### 3. Install Required Plugins

Install the following plugins in Jenkins:
- Git Plugin
- Pipeline Plugin
- ShiningPanda Plugin

### 4. Configure GitHub Credentials

Add your GitHub credentials in Jenkins to allow access to the repository.

## GitHub Actions Workflows

### CI Pipeline (.github/workflows/ci.yml)

This workflow runs on every push and pull request to the main branch:
- Sets up a PostgreSQL database service
- Installs Python dependencies
- Runs Django migrations
- Executes tests
- Performs code quality checks with flake8
- Generates code coverage reports

### Deployment Pipeline (.github/workflows/dep.yml)

This workflow builds and pushes Docker images to Docker Hub:
- Builds Docker image using the provided Dockerfile
- Pushes images to Docker Hub with latest tag and commit SHA tag
- Uses GitHub Secrets for Docker credentials

## Environment Variables

The following environment variables need to be set in GitHub Secrets:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password
- `DJANGO_SECRET_KEY`: Django secret key for the application
- `CODECOV_TOKEN`: Token for uploading coverage reports to Codecov (optional)

## Jenkinsfile

The Jenkinsfile contains the pipeline configuration for:
- Checking out code from GitHub
- Setting up the Python environment
- Running tests with pytest
- Generating test reports
- Building and pushing Docker images
