<div align="center">

  <img src="assets/logo.png" alt="logo" width="500" height="auto" />
  <h1>Greenroom: Your Backend Factory for AI-Powered Applications</h1>
  
  <p>
    A boilerplate project designed to accelerate the development of AI-powered applications and robust data pipelines.
  </p>
  
<!-- Badges -->
<p>
  <a href="https://github.com/puneetshrivas/greenroom/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/puneetshrivas/greenroom" alt="contributors" />
  </a>
  <a href="">
    <img src="https://img.shields.io/github/last-commit/puneetshrivas/greenroom" alt="last update" />
  </a>
  <a href="https://github.com/puneetshrivas/greenroom/network/members">
    <img src="https://img.shields.io/github/forks/puneetshrivas/greenroom" alt="forks" />
  </a>
  <a href="https://github.com/puneetshrivas/greenroom/stargazers">
    <img src="https://img.shields.io/github/stars/puneetshrivas/greenroom" alt="stars" />
  </a>
  <a href="https://github.com/puneetshrivas/greenroom/issues/">
    <img src="https://img.shields.io/github/issues/puneetshrivas/greenroom" alt="open issues" />
  </a>
  <a href="https://github.com/puneetshrivas/greenroom/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/puneetshrivas/greenroom.svg" alt="license" />
  </a>
</p>
   
<h4>
    <a href="https://github.com/puneetshrivas/greenroom/">View Demo</a>
  <span> · </span>
    <a href="https://github.com/puneetshrivas/greenroom">Documentation</a>
  <span> · </span>
    <a href="https://github.com/puneetshrivas/greenroom/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/puneetshrivas/greenroom/issues/">Request Feature</a>
  </h4>
</div>

<br />

<!-- Table of Contents -->
# :notebook_with_decorative_cover: Table of Contents

- [:notebook\_with\_decorative\_cover: Table of Contents](#notebook_with_decorative_cover-table-of-contents)
  - [:star2: About the Project](#star2-about-the-project)
    - [:space\_invader: Tech Stack](#space_invader-tech-stack)
    - [:dart: Key Features](#dart-key-features)
  - [:toolbox: Getting Started](#toolbox-getting-started)
    - [:bangbang: Prerequisites](#bangbang-prerequisites)
    - [:gear: Installation](#gear-installation)
  - [:triangular\_flag\_on\_post: Deployment](#triangular_flag_on_post-deployment)
  - [:wave: Contributing](#wave-contributing)

<!-- About the Project -->
## :star2: About the Project

Greenroom is a boilerplate project designed to accelerate the development of AI-powered applications and robust data pipelines. It seamlessly integrates a powerful tech stack to empower you with:

### :space_invader: Tech Stack
- **Python**: The foundation for our backend services.
- **FastAPI**: A high-performance framework for building APIs.
- **LangChain**: Simplifies working with language models and data sources.
- **Docker**: Containerization for seamless deployment.
- **ChromaDB, Elasticsearch, Firestore**: Choose the database that best suits your needs.
- **Selenium**: Web scraping capabilities.
- **Google Sheets API**: Integrate with spreadsheets for data input/output.
- **(Optional) Celery**: Task queue for background processes and scheduling.

### :dart: Key Features
- **Rapid API Development**: Effortlessly build RESTful endpoints for Retrieval-Augmented Generation (RAG), custom backend processes, and database interactions.
- **Data Ingestion**: Streamline data collection via web scraping with Selenium and Google Sheets integrations.
- **Data Management**: Powerful filtering and search with Elasticsearch, automated database maintenance (cron jobs).
- **Deployment & Observability**: Docker-based deployment for consistency, robust logging and testing architecture.
- **Modular Structure**: Clearly organized modules for API endpoints, data pipelines, and database operations.
- **Example Implementations**: Get started quickly with code examples for RAG, web scraping, data filtering, etc.
- **Configuration**: Easily adjust settings for databases, logging, and scraping targets.
- **Testing Framework**: Included tests ensure the reliability of your application.
- **Scalability**: Designed to grow with your needs.

## :toolbox: Getting Started

### :bangbang: Prerequisites
This project requires Docker and Python installed on your local machine.

### :gear: Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/puneetshrivas/greenroom.git
2. Navigate to the project directory:
    ```bash
    cd greenroom
3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt

### :wrench: Configuration
Update the configuration files in config/ according to your setup.

### :running: Running the Project
1. For Development:
    ```bash
    docker-compose up
2. For Production:
    ```bash
    See deployment instructions below.

## :file_folder: Project Structure
```bash
greenroom/
├── Dockerfile                          # Docker configuration for containerization
├── README.md                           # Project documentation
├── app/                                # Application source code
│   ├── models/                         # Data models
│   └── process/                        # Data processing modules
│       └── dress_description/          # Specific processing for dress descriptions
│           ├── functions.py            # Core functions for processing
│           ├── main.py                 # Main processing script
│           └── routes.py               # API routes for dress description processing
├── core/                               # Core functionalities and utilities
│   ├── common_modules/                 # Shared modules and tools
│   │    ├── file_tools.py              # File handling utilities
│   │    ├── image_tools.py             # Image processing utilities
│   │    ├── json_tools.py              # JSON handling utilities
│   │    └── routes_populate.py         # Utilities for populating routes
│   └── server.py                       # Server configuration and initialization
├── data/                               # Data handling modules
│   ├── firestore/                      # Firestore database interactions
│   │    └── main.py                    # Firestore operations script
│   ├── sheetsdb/                       # Google Sheets interactions
│   ├── blogs/                          # Blog-related data handling
│   │    └── populate_blogs.py          # Script for populating blog data
│   └── prompts/                        # Prompt-related data handling
│       ├── populate_prompts.py         # Script for populating prompt data
│       └── prompts_sheets.csv          # CSV file for prompt data
├── main.py                             # Main entry point for the application
├── requirements.txt                    # Project dependencies
└── testing/                            # Testing modules
    └── manual_tests/                   # Manual testing scripts
        └── test_endpoint.ipynb         # Jupyter notebook for endpoint testing
 ```
## :triangular_flag_on_post: Deployment
Greenroom is optimized for Docker-based deployment. You can use a cloud platform (AWS, GCP, Azure) or your own infrastructure. Detailed instructions can be found in docs/deployment.md.

## :wave: Contributing
Contributions are always welcome!

See CONTRIBUTING.md for ways to get started.

<!-- License -->
:warning: License
This project is licensed under the [Choose License] License.