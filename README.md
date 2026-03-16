# BiOS: Biodiversity Observatory System

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)

BiOS is an open-source framework designed for the integration and management of heterogeneous biodiversity data.

## Citation

If you use BiOS in your research, please cite the following article:

> Roldan, A., Duran, T. G., Far, A. J., Capa, M., Arboleda, E., & Cancellario, T. (2026). BiOS: An Open-Source Framework for the Integration of Heterogeneous Biodiversity Data. _bioRxiv_, 2026-02.

## System Overview

The BiOS framework consists of a PostGIS and Django-based back-end interconnected with a Next.js front-end. The architecture is modular and highly decoupled, providing a robust RESTful API to manage diverse biodiversity data.

The underlying database architecture leverages Django's Object-Relational Mapping (ORM) and is logically divided into six thematic modules: **Taxonomy**, **Occurrences**, **Genetics**, **Tags**, **Geography**, and **Versioning**. These interconnected modules guarantee structural integrity, flexible spatial querying, data standardisation, and strict traceability.

## Quick Installation

To ensure consistency between development and production environments, the BiOS framework relies on Docker containers.

### 1. Deploying the Back-end

Clone the back-end repository and configure your environment variables:

```bash
git clone https://github.com/centrebalearbiodiversitat/BiOS_backend.git
cd BiOS_backend
cp .env_template .env
```

Build the Docker image and launch the services:

```bash
# For development environments
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml up --build

# For production environments
sudo docker compose -f docker-compose.yml up --build
```

Execute database migrations and create an administrative user:

```bash
# Open a bash session inside the Django container
sudo docker compose -f docker-compose.local.yml exec django bash

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

Once running, the API is accessible at `http://localhost:8000/api/v1/`, and the interactive OpenAPI (Swagger) documentation is available at `http://localhost:8000/api/docs/`.

### 2. Standardised Data Ingestion

The framework provides an automated bulk ingestion workflow that ensures data validation and resolves relational constraints. Inside the Django container, execute the following script to load data grouped by geographical data, base catalogs, taxonomy, occurrences, and genetics:

```bash
sh load_db.sh
```

### 3. Deploying the Front-end

In a separate terminal, clone the Next.js front-end module and install the required dependencies:

```bash
git clone https://github.com/centrebalearbiodiversitat/BiOS_frontend.git
cd BiOS_frontend

# Install dependencies
npm install

# Configure environment
cp .env.template .env
```

Start the development server:

```bash
npm run dev
```

The web interface will be accessible at `http://localhost:3000`.

## Contributing Guidelines

### 1. Local Preparation

**Clone the repository**: If you do not yet have a local copy of the project, clone the repository from GitHub:

```bash
git clone https://github.com/centrebalearbiodiversitat/BiOS_backend.git
```

**Create a new branch**: Before making any changes, create a new branch based on the main development branch (`dev`) to isolate your modifications:

### 2. Implementation

Make the necessary conceptual or code changes.

### 3. Commit Changes

Add your modified files and write a clear, standard-compliant message describing your changes:

```bash
git add .
git commit -m "feat(geography): implement Balearic municipalities"
```

> [!IMPORTANT]
> To maintain a clean, automated Git history, this project adopts [Semantic Versioning (SemVer)](https://semver.org/) and [Conventional Commits](https://www.conventionalcommits.org/). Commit messages must follow the structure: `type(scope): short message` (e.g., `feat`, `fix`, `docs`, `refactor`).

### 4. Push to Remote and Create a Pull Request

Push your isolated branch to the remote repository:

```bash
git push origin <branch-name>
```

Finally, access GitHub and open a Pull Request against the `dev` branch, providing a concise summary of the implementations and assigning appropriate reviewers.
