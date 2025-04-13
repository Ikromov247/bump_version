# Contributing to Version Bumper

Thank you for your interest in contributing to Version Bumper!
This document provides guidelines and instructions for contributing to this project.

## Project Overview

Version Bumper is a tool for automating version number updates in project files, supporting both CLI usage and GitHub Actions workflows.
The main objective is to make updating version number easier.
This is mostly a pet project, so feel free to contribute whatever!

## Getting Started

### Prerequisites
- Python 3.6+
- Git
- PyYAML
- pre-commit
- black

### Development Setup
1. Clone the repository
2. Install the dependencies:
    - `pip install -r requirements.txt`
    - `pip install -r requirements-dev.txt`
3. Install commit hooks: `pre-commit install`


### Contribution Workflow
1. Create a new branch for your changes: `git checkout -b feature/your-feature-name`
2. Make your changes and ensure tests pass
3. Commit your changes with a descriptive message
4. Push your branch and create a pull request

### Pull Request Guidelines
- Provide a clear description of the changes
- Include any relevant issue numbers
- Ensure all tests pass
- Follow the code style guidelines


### Code Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Maintain type hints for all functions
- Keep functions focused on a single responsibility

### Documentation

Please update documentation when changing functionality:
- Update the README.md for user-facing changes
- Update docstrings for all new or modified functions
- Add examples for new features
