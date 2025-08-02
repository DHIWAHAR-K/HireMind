# HireMind: Agentic AI Application for HR Hiring Process Planning

## Assignment Requirements

This project was built to fulfill the following assignment:

**Objective:** Build an Agentic AI App that assists an HR professional in planning a hiring process for a startup.

**Requirements:**
1. Use tools like LangGraph, LangChain Agents, or OpenAI Function Calling
2. Demonstrate multi-step reasoning, tool simulation/integration, and memory retention
3. Bonus: Incorporate a frontend, analytics, or any creative enhancements

## What I Built

HireMind is an AI-powered hiring process automation platform that fully addresses each requirement:

### Requirement 1: AI Frameworks
- **LangGraph**: Implements a sophisticated state machine orchestrating 6 specialized agents
- **LangChain Agents**: Each agent uses LangChain for structured reasoning
- **OpenAI Function Calling**: Integrated tools for timeline estimation, salary benchmarking, and offer generation

### Requirement 2: Core Capabilities
- **Multi-step Reasoning**: 6 sequential agents that build upon each other's outputs
- **Tool Integration**: Custom tools for timeline calculation, salary data, and offer templates
- **Memory Retention**: Redis-based persistence for conversation context and workflow state

### Requirement 3: Bonus Features
- **React Frontend**: Real-time progress tracking with Material-UI
- **Performance Metrics**: Dashboard showing hiring statistics and success rates
- **Authentication System**: Secure user accounts with SQLite backend

## Key Features

### 1. Six Specialized AI Agents
Each agent is powered by OpenAI GPT-4 and handles a specific aspect of the hiring process:

1. **Role Definition Agent**: Transforms natural language requirements into structured role specifications
2. **JD Generator Agent**: Creates comprehensive, bias-free job descriptions
3. **Interview Planner Agent**: Designs multi-stage interview processes with evaluation criteria
4. **Timeline Estimator**: Calculates realistic hiring timelines (using simulated market data)
5. **Salary Benchmarking Agent**: Provides compensation recommendations (using simulated data)
6. **Offer Letter Generator**: Creates professional offer letter templates

### 2. Technical Implementation
- **LangGraph Workflow**: State machine managing the entire hiring pipeline
- **Asynchronous Processing**: FastAPI backend with background tasks for non-blocking execution
- **Real-time Updates**: Frontend polls for progress updates every 2 seconds
- **Persistent Storage**: Redis for session management and SQLite for user authentication
- **JWT Authentication**: Secure API endpoints with token-based auth

### 3. User Interface
- **Modern Dashboard**: Shows active hirings, completion stats, and recent activities
- **Hiring Wizard**: Multi-step form with real-time progress visualization
- **Agent Playground**: Test individual agents without running full workflow
- **Profile Management**: View and manage all created hiring profiles

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         React Frontend                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Dashboard  │  │ New Hiring   │  │  Agent Playground   │  │
│  │             │  │   Wizard     │  │                     │  │
│  └─────────────┘  └──────────────┘  └─────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴─────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              LangGraph Workflow Engine                │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐ │   │
│  │  │Role │→ │ JD  │→ │Inter│→ │Time │→ │Sal. │→ │Offer│ │   │
│  │  │Def. │  │Gen. │  │view │  │line │  │Bench│  │Gen. │ │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘ │   │
│  └───────────────────────────────────────────────────────┘   │
│                             │                                │
│  ┌───────────────┐  ┌───────┴────────┐  ┌──────────────────┐ │
│  │  Redis Store  │  │ OpenAI Tools   │  │ Background Tasks │ │
│  │  (Memory)     │  │ (Functions)    │  │ (Async Workers)  │ │
│  └───────────────┘  └────────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## What's Honest About This Implementation

### Actually Implemented
- 6 AI agents with full LangGraph orchestration
- Real-time progress tracking with polling mechanism
- Redis memory persistence for workflow state
- FastAPI async background processing
- React frontend with Material-UI design
- SQLite + JWT authentication system
- Agent playground for testing
- Complete hiring workflow from role definition to offer letter

### Uses Simulated Data
- **Salary Benchmarking**: Returns mock salary ranges (not connected to real APIs)
- **Timeline Estimation**: Uses predefined estimates (not based on real market data)
- **Offer Templates**: Generated using AI, not legal templates

### Future Enhancements
- Real salary API integration (Glassdoor, Salary.com)
- Analytics dashboard with charts
- Docker containerization
- WebSocket for real-time updates (replacing polling)
- PDF export functionality
- Email integration

## Technology Stack

- **Backend**: Python 3.8+, FastAPI, LangGraph, LangChain, Redis
- **Frontend**: React 18, TypeScript, Material-UI, Redux Toolkit
- **AI/ML**: OpenAI GPT-4, Function Calling
- **Database**: SQLite (auth), Redis (sessions)
- **Authentication**: JWT tokens with secure session management

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis server
- OpenAI API key

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/HireMind.git
cd HireMind
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env

# Start Redis
redis-server

# Run backend
uvicorn api.main:app --reload --port 8000
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the Application**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Usage Guide

### Starting a New Hiring Process
1. Login or create an account
2. Navigate to Dashboard → "New Hiring"
3. Enter company name and role description
4. Watch real-time progress as each AI agent completes its task
5. View the complete hiring package when finished

### Using Agent Playground
- Test individual agents without running the full workflow
- Select an agent type and provide input
- See immediate results from that specific agent

## API Documentation

### Key Endpoints

```http
POST /api/auth/register
POST /api/auth/login
POST /api/workflow/start
GET /api/workflow/{session_id}
POST /api/agent/run
GET /api/profiles
```

Full API documentation available at http://localhost:8000/docs

## Testing

Run the test suite:
```bash
cd backend
pytest tests/ -v
```

Current test files:
- `test_models.py` - Data model validation
- `test_agents.py` - Individual agent testing
- `test_workflows.py` - Workflow orchestration
- `test_api.py` - API endpoint testing
- `test_tools.py` - Tool functionality

## Project Structure

```
HireMind/
├── backend/
│   ├── api/              # FastAPI routes and main app
│   ├── src/
│   │   ├── agents/       # 6 specialized AI agents
│   │   ├── workflows/    # LangGraph workflow engine
│   │   ├── tools/        # Function calling tools
│   │   ├── memory/       # Redis memory management
│   │   └── models/       # Pydantic models
│   └── tests/            # Test suite
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages
│   │   ├── components/   # Reusable components
│   │   ├── services/     # API integration
│   │   └── store/        # Redux state management
│   └── package.json
└── README.md
```

## Acknowledgments

This project was built as a demonstration of modern AI application development, showcasing:
- Multi-agent AI systems with LangGraph
- Real-time web applications with React
- Asynchronous Python backends with FastAPI
- State management and persistence strategies

## License

This project is provided as-is for educational and evaluation purposes.