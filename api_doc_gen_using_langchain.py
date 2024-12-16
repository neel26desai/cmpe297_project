# -*- coding: utf-8 -*-
"""api_doc_gen_using_langhchain.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1B50rgMuWRoagKGJ1ql51zVKmydUB5uJs

# The content of this file consist of:

A script (api_doc_gen_v2.py) that generates API documentation dynamically.
The script will:
Take an API file path as input.
Save the documentation as a Markdown file to a given output path.
Allow two modes: Generate for all APIs (entire file) or API by API based on user input.
"""

# Create .env file dynamically in Colab
# with open('.env', 'w') as f:
#     f.write("OPENAI_API_KEY=your_api_key")

import os
import sys
import argparse
import importlib.util
from fastapi.routing import APIRoute
from fastapi import FastAPI
import inspect
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI  # Updated import for ChatOpenAI


# ==============================
# Environment Setup
# ==============================

# Load environment variables
load_dotenv()

# OpenAI API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key not set. Ensure it's defined in the .env file.")

# Initialize LangChain LLM
llm = ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY, temperature=0)

# Define LangChain Prompt Template
prompt_template = PromptTemplate(
    input_variables=["api_name", "path", "methods", "parameters", "function_content", "description"],
    template="""
    Generate detailed and structured API documentation for the following endpoint:
    - API Name: {api_name}
    - Path: {path}
    - Methods: {methods}
    - Parameters: {parameters}
    - Function Content:
    {function_content}
    - Description: {description}
    """
)


# ==============================
# Utility Functions
# ==============================

def load_api_file(file_path):
    """
    Dynamically loads the provided FastAPI app file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"API file not found: {file_path}")
    spec = importlib.util.spec_from_file_location("api_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract_routes_fastapi(app):
    """
    Extracts route details from a FastAPI app instance.
    """
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = list(route.methods)
            path = route.path
            api_name = route.name or "Unnamed API"
            parameters = [param.name for param in route.dependant.path_params]
            function_content = inspect.getsource(route.endpoint).strip() if route.endpoint else "No source code available"
            description = route.endpoint.__doc__ or "No description available."

            routes.append({
                "api_name": api_name,
                "path": path,
                "methods": methods,
                "parameters": parameters,
                "function_content": function_content,
                "description": description
            })
    return routes


# ==============================
# API Documentation Generation
# ==============================

def generate_documentation(route):
    """
    Generates API documentation for a given route using LangChain.
    """
    chain = LLMChain(llm=llm, prompt=prompt_template)
    input_data = {
        "api_name": route["api_name"],
        "path": route["path"],
        "methods": ", ".join(route["methods"]),
        "parameters": ", ".join(route["parameters"]) if route["parameters"] else "None",
        "function_content": route["function_content"],
        "description": route["description"]
    }
    return chain.run(input_data)

def generate_full_api_doc(routes):
    """
    Generates API documentation for all routes at once.
    """
    documentation = []
    for route in routes:
        doc = generate_documentation(route)
        documentation.append(doc)
    return documentation

def generate_api_by_api(routes):
    """
    Generates documentation interactively, API by API.
    """
    documentation = []
    selected_routes = []
    for route in routes:
        choice = input(f"Include documentation for '{route['path']}'? (y/n): ").lower()
        if choice == "y":
            doc = generate_documentation(route)
            documentation.append(doc)
            selected_routes.append(route)
    return selected_routes, documentation

# ==============================
# File Handling Functions
# ==============================

def save_to_markdown(routes, documentation, output_path):
    """
    Saves generated API documentation to a Markdown file.
    """
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# Comprehensive API Documentation\n\n")
        for route, doc in zip(routes, documentation):
            f.write(f"## API Name: {route['api_name']}\n")
            f.write(f"**Path**: {route['path']}\n")
            f.write(f"**Methods**: {', '.join(route['methods'])}\n")
            f.write(f"**Parameters**: {', '.join(route['parameters']) if route['parameters'] else 'None'}\n\n")
            f.write(f"**Function Content**:\n```\n{route['function_content']}\n```\n\n")
            f.write(f"**Description**: {route['description']}\n\n")
            f.write(f"**Generated Documentation**:\n{doc}\n\n")
    print(f"✅ Documentation saved to: {output_path}")


# ==============================
# Main Program Execution
# ==============================

def main():
    """
    Main function to handle user input and execute the documentation generation logic.
    """
    parser = argparse.ArgumentParser(description="Generate API Documentation")
    parser.add_argument("--api_file_path", type=str, required=True, help="Path to the API file")
    parser.add_argument("--output_markdown_path", type=str, required=True, help="Output markdown file path")
    parser.add_argument("--framework", type=str, choices=["fastapi", "flask"], default="fastapi", help="Framework")
    parser.add_argument("--mode", type=int, choices=[1, 2], required=True,
                    help="1: Generate for the entire file, 2: API-by-API interactive mode")
    args = parser.parse_args()

    # Load API file and app
    module = load_api_file(args.api_file_path)
    app = getattr(module, "app", None)
    if not app or not isinstance(app, FastAPI):
        raise ValueError("No FastAPI app instance found.")

    # Extract routes
    routes = extract_routes_fastapi(app)

    # Prompt the user to choose the documentation type
    print("\nChoose mode for API documentation generation:")
    print("1. Generate documentation for the entire file.")
    print("2. Generate documentation API-by-API (interactive mode).")

    while True:
        try:
            mode = int(input("Enter 1 or 2: ").strip())
            if mode not in [1, 2]:
                raise ValueError("Invalid input. Please enter 1 or 2.")
            break
        except ValueError as e:
            print(e)

    # Generate documentation based on user's choice
    documentation = []
    if mode == 1:
        print("\nGenerating documentation for the entire file...")
        documentation = generate_full_api_doc(routes)
    elif mode == 2:
        print("\nGenerating documentation API-by-API (Interactive Mode)...")
        routes, documentation = generate_api_by_api(routes)

    # Save to file
    save_to_markdown(routes, documentation, args.output_markdown_path)

    # Confirm output
    if os.path.exists(args.output_markdown_path):
        print(f"\n✅ Documentation successfully saved to: {args.output_markdown_path}")
    else:
        print("\n❌ Failed to save the documentation file.")

if __name__ == "__main__":
    main()

# """To view the content of generated file."""

# !cat /content/output_docs/api_docs.md

# !ls /content/

# !zip -r /content/output_docs.zip /content/output_docs

# !ls /content/

# from google.colab import files
# files.download('/content/output_docs.zip')
