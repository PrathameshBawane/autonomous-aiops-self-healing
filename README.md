# Autonomous AIOps – Multi-Agent Self-Healing System

An academic prototype demonstrating a basic multi-agent AIOps workflow for detecting server errors, analyzing logs, generating possible fixes, validating them in a Docker sandbox, and sending the result for human approval.

**Project Status:** Academic prototype / basic implementation  
**Development:** Manual development  
**Note:** This project is not intended to represent a production-grade autonomous self-healing system.

## Overview

Modern applications generate large amounts of logs, making manual error detection and troubleshooting time-consuming.

This project demonstrates how multiple AI agents can work together to automate parts of the incident-resolution process.

The workflow is:

Application / Server  
↓  
Log File  
↓  
Sentry Agent  
↓  
Librarian Agent  
↓  
Architect Agent  
↓  
Safety Officer  
↓  
Docker Sandbox Validation  
↓  
Human Approval  
↓  
Apply Fix
     
## Multi-Agent Workflow

1. Sentry Agent

- Detects errors or failures from the available application/server logs.

2. Librarian Agent

- Analyzes the logs and helps identify the possible cause of the detected problem.

3. Architect Agent

- Uses an AI model to generate a possible fix based on the analyzed problem.

4. Safety Officer

- Tests and validates the generated fix in an isolated Docker environment before it is considered for application.

5. Human Approval

- The proposed fix is presented for human review. The administrator can approve or reject the proposed action.

## Technologies Used

- Python
- LangGraph
- Mistral AI
- Gemini
- Docker
- Multi-Agent AI
- Log Analysis
- DevOps Automation

## Key Features

- Multi-agent workflow
- Log-based error detection
- Automated log analysis
- AI-generated fix suggestions
- Docker-based validation
- Human approval before applying a fix
- Feedback/retry workflow

## Project Architecture

The system consists of four main agents:

Sentry  
↓  
Librarian  
↓  
Architect  
↓  
Safety Officer  
↓  
Human Administrator  

LangGraph is used to coordinate the workflow between the agents.

## Project Demo

[▶ Watch the Project Demo](demo/aiops-demo.mp4)

## Project Scope

This implementation is a basic academic prototype intended to demonstrate the concept of multi-agent AIOps and self-healing workflows.

It does not attempt to provide a complete production-ready autonomous infrastructure management system.

Possible future improvements include:

- More reliable fault detection
- Better root-cause analysis
- Integration with real monitoring systems
- Improved validation and rollback mechanisms
- Observability dashboards
- More robust security controls
- Integration with cloud infrastructure
- Better handling of complex incidents

## Team
- Prathamesh Bawane
- Rohit Pathe
- Sagar Shrivas
- Rohit Ninawe

**Department:** Artificial Intelligence  
**Institute:** G H Raisoni College of Engineering  
**Year:** 2026

# Disclaimer

This repository contains an academic project developed as a learning prototype.

The implementation should not be considered a production-ready autonomous infrastructure management system.
