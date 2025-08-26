# LTV-Agent

LTV-Agent is a FastAPI-based application that provides an API for analyzing news articles and determining their veracity. It uses a microservices architecture and a multi-step analysis process to provide a comprehensive assessment of the credibility of a news article.

![Inicio de la aplicación](/caps/start.png)
![Inicio de la aplicación](/caps/running.png)
![Inicio de la aplicación](/caps/end.png)

## Features

-   **Multi-step analysis:** The agent performs a comprehensive analysis of a news article, including keyword extraction, related article search, inference, and confidence scoring.
-   **Microservices architecture:** The project is built using a microservices architecture, which makes it scalable and easy to maintain.
-   **HTTP and WebSocket APIs:** The agent provides both HTTP and WebSocket APIs for analyzing news articles.
-   **Containerized:** The project is containerized using Docker and Docker Compose, which makes it easy to deploy and run.

## Getting Started

To get started with the LTV-Agent, you will need to have Docker and Docker Compose installed. Once you have these installed, you can follow these steps:

1.  Clone the repository:

```bash
git clone https://github.com/carlosDAC2020/LTV-Agent.git
```

2.  Create a `.env` file in the root of the project and add the following environment variables:

```
LTV_API=ltv_api
BRAVE_MCP=brave_mcp
LTV_MCP=ltv_mcp
BRAVE_API_KEY=your-brave-api-key
GEMINI_API_KEY=your-gemini-api-key
```

3.  Run the following command to start the application:

```bash
docker-compose up -d

docker-compose logs -f
```

To view the logs of a specific service (e.g., `ltv-agent`):

```bash
docker-compose logs -f ltv-agent
```

## Usage

Once the application is running, you can use the following API endpoints to analyze news articles:

### HTTP API

To analyze a news article using the HTTP API, you can send a POST request to the `/agent/ltv/http` endpoint with the following JSON payload:

```json
{
    "text": "The text of the news article to analyze."
}
```

### WebSocket API

To analyze a news article using the WebSocket API, you can connect to the `/agent/ltv/ws` endpoint and send a JSON message with the following format:

```json
{
    "text": "The text of the news article to analyze."
}
```

The WebSocket API will then send you a series of messages with the results of each step of the analysis process.

## Project Structure

The project is structured as follows:

```
├── app
│   ├── core
│   ├── data
│   ├── models
│   ├── routers
│   └── services
├── ltv_mcp
├── static
└── templates
```

-   `app`: This directory contains the main FastAPI application.
-   `ltv_mcp`: This directory contains the microservice for calculating semantic context and veracity scores.
-   `static`: This directory contains the static files for the web interface.
-   `templates`: This directory contains the templates for the web interface.

## API Endpoints

The following API endpoints are available:

-   `POST /agent/ltv/http`: Analyzes a news article and returns the results in a single response.
-   `WS /agent/ltv/ws`: Analyzes a news article and returns the results of each step of the analysis process in a series of WebSocket messages.

