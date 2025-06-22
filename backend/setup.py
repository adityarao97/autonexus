#!/usr/bin/env python3
"""
Setup script for Raw Material Sourcing Workflow
A comprehensive MCP-agent workflow for raw material sourcing analysis
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    sys.exit("Error: Raw Material Sourcing Workflow requires Python 3.8 or later.")

# Get the directory containing this setup.py file
HERE = Path(__file__).parent
README_PATH = HERE / "README.md"
REQUIREMENTS_PATH = HERE / "requirements.txt"
VERSION_PATH = HERE / "VERSION"

def read_file(filepath: Path) -> str:
    """Read content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def read_requirements() -> list:
    """Read requirements from requirements.txt file."""
    if REQUIREMENTS_PATH.exists():
        with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    # Handle git+https:// URLs and -e flags
                    if line.startswith("-e ") or line.startswith("git+"):
                        continue
                    # Handle version specifiers
                    requirements.append(line)
            return requirements
    return []

def get_version() -> str:
    """Get version from VERSION file or default."""
    if VERSION_PATH.exists():
        return read_file(VERSION_PATH)
    return "1.0.0"

def get_long_description() -> str:
    """Get long description from README file."""
    if README_PATH.exists():
        return read_file(README_PATH)
    return """
Raw Material Sourcing Workflow

A comprehensive MCP-agent workflow system for analyzing raw material sourcing options
using multi-agent collaboration with Leader, Country, and Expert agents.

Features:
- Multi-agent coordination for comprehensive analysis
- Integration with DuckDuckGo search, Claude LLM, and MySQL database
- Automated scoring and recommendation generation
- Risk assessment and mitigation strategies
- Implementation guidance and business impact analysis
"""

# Core requirements that are always needed
CORE_REQUIREMENTS = [
    "aiohttp>=3.8.0",
    "aiomysql>=0.1.1",
    "asyncio-mqtt>=0.11.0",
    "python-dateutil>=2.8.0",
    "typing-extensions>=4.0.0",
]

# MCP requirements
MCP_REQUIREMENTS = [
    "mcp>=0.1.0",
]

# Optional requirements for enhanced functionality
OPTIONAL_REQUIREMENTS = {
    "nlp": [
        "nltk>=3.8",
        "spacy>=3.4.0",
        "textblob>=0.17.0",
    ],
    "monitoring": [
        "prometheus-client>=0.15.0",
        "grafana-api>=1.0.0",
    ],
    "security": [
        "cryptography>=3.4.0",
        "PyJWT>=2.4.0",
        "bcrypt>=3.2.0",
    ],
    "performance": [
        "uvloop>=0.17.0",
        "orjson>=3.8.0",
        "cython>=0.29.0",
    ],
    "data": [
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scipy>=1.9.0",
    ],
    "visualization": [
        "matplotlib>=3.5.0",
        "plotly>=5.10.0",
        "seaborn>=0.11.0",
    ]
}

# Development requirements
DEV_REQUIREMENTS = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.8.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "isort>=5.10.0",
    "pre-commit>=2.20.0",
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "coverage>=6.5.0",
]

# Testing requirements
TEST_REQUIREMENTS = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.8.0",
    "pytest-xdist>=2.5.0",
    "factory-boy>=3.2.0",
    "faker>=15.0.0",
]

# Documentation requirements
DOCS_REQUIREMENTS = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "sphinx-autodoc-typehints>=1.19.0",
    "myst-parser>=0.18.0",
]

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        print("\n🎉 Development installation completed!")
        print("Next steps:")
        print("1. Set up your database: mysql -u root -p < database/schema.sql")
        print("2. Configure your API keys in config/config.py")
        print("3. Run tests: pytest")
        print("4. Start developing: python workflow_orchestrator.py")

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        print("\n🎉 Installation completed!")
        print("Next steps:")
        print("1. Set up your database: mysql -u root -p < database/schema.sql")
        print("2. Configure your API keys in config/config.py")
        print("3. Run the workflow: python workflow_orchestrator.py")

# Package metadata
PACKAGE_NAME = "raw-material-sourcing-workflow"
VERSION = get_version()
AUTHOR = "Raw Material Sourcing Team"
AUTHOR_EMAIL = "team@rawmaterialsourcing.com"
DESCRIPTION = "Multi-agent workflow for raw material sourcing analysis"
LONG_DESCRIPTION = get_long_description()
URL = "https://github.com/yourusername/raw-material-sourcing-workflow"
LICENSE = "MIT"

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business :: Financial",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Framework :: AsyncIO",
    "Environment :: Console",
    "Natural Language :: English",
]

# Keywords for better discoverability
KEYWORDS = [
    "sourcing", "supply-chain", "raw-materials", "agents", "mcp", "workflow",
    "analysis", "recommendation", "automation", "business-intelligence",
    "risk-assessment", "sustainability", "cost-optimization"
]

# Project URLs
PROJECT_URLS = {
    "Homepage": URL,
    "Documentation": f"{URL}/docs",
    "Source Code": URL,
    "Bug Reports": f"{URL}/issues",
    "Feature Requests": f"{URL}/issues",
    "Changelog": f"{URL}/blob/main/CHANGELOG.md",
    "Contributing": f"{URL}/blob/main/CONTRIBUTING.md",
}

# Console scripts for command-line usage
CONSOLE_SCRIPTS = [
    "sourcing-workflow=workflow_orchestrator:main",
    "sourcing-demo=run_workflow:main",
    "sourcing-config=config.config:main",
]

# Entry points for plugin system
ENTRY_POINTS = {
    "console_scripts": CONSOLE_SCRIPTS,
    "sourcing_workflow.agents": [
        "leader = agents.leader_agent:LeaderAgent",
        "country = agents.country_agent:CountryAgent",
        "expert = agents.expert_agent:ExpertAgent",
    ],
    "sourcing_workflow.tools": [
        "duckduckgo = tools.duckduckgo_tool:DuckDuckGoTool",
        "claude = tools.claude_tool:ClaudeTool",
        "mysql = tools.mysql_tool:MySQLTool",
    ],
}

# Package data to include
PACKAGE_DATA = {
    "": [
        "*.md",
        "*.txt",
        "*.yml",
        "*.yaml",
        "*.json",
        "*.sql",
        "*.env.example",
    ],
    "database": ["*.sql"],
    "config": ["*.py", "*.json", "*.yaml"],
    "docs": ["*.md", "*.rst"],
    "examples": ["*.py", "*.json"],
    "tests": ["*.py", "data/*.json"],
}

# Additional data files to include
DATA_FILES = [
    ("database", ["database/schema.sql"]),
    ("config", ["config/config.py"]),
    ("docs", ["README.md", "CHANGELOG.md"]),
]

def main():
    """Main setup function."""
    
    # Combine all requirements
    install_requires = CORE_REQUIREMENTS + MCP_REQUIREMENTS + read_requirements()
    
    # Remove duplicates while preserving order
    seen = set()
    install_requires = [x for x in install_requires if not (x in seen or seen.add(x))]
    
    # Create extras_require dictionary
    extras_require = OPTIONAL_REQUIREMENTS.copy()
    extras_require.update({
        "dev": DEV_REQUIREMENTS,
        "test": TEST_REQUIREMENTS,
        "docs": DOCS_REQUIREMENTS,
        "all": list(set(
            sum(OPTIONAL_REQUIREMENTS.values(), []) +
            DEV_REQUIREMENTS +
            TEST_REQUIREMENTS +
            DOCS_REQUIREMENTS
        )),
    })
    
    # Setup configuration
    setup(
        # Basic package information
        name=PACKAGE_NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url=URL,
        project_urls=PROJECT_URLS,
        license=LICENSE,
        
        # Package discovery
        packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        include_package_data=True,
        
        # Dependencies
        install_requires=install_requires,
        extras_require=extras_require,
        python_requires=">=3.8",
        
        # Entry points
        entry_points=ENTRY_POINTS,
        
        # Classification
        classifiers=CLASSIFIERS,
        keywords=", ".join(KEYWORDS),
        
        # Options
        zip_safe=False,
        platforms=["any"],
        
        # Custom commands
        cmdclass={
            "develop": PostDevelopCommand,
            "install": PostInstallCommand,
        },
        
        # Test configuration
        test_suite="tests",
        tests_require=TEST_REQUIREMENTS,
        
        # Additional metadata for modern setuptools
        setup_requires=["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"],
    )

if __name__ == "__main__":
    main()