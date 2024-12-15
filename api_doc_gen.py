# -*- coding: utf-8 -*-
"""297-project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bxDZUiLvoMOL9fc4W3aldZDSD-uqCbHL
"""

pip install fastapi uvicorn markdown2

!pip install openai==0.28

from google.colab import drive
drive.mount('/content/drive')

api_file_path = "/content/drive/My Drive/297-project-api-documentation-generator/sample_apis.py"
output_markdown_path = "/content/drive/My Drive/297-project-api-documentation-generator/api_docs.md"

"""**Step 1: Extract API Details**"""

pip install --upgrade langchain

pip install langchain-community

def extract_api_details(file_path, framework):
    import importlib.util
    from fastapi.routing import APIRoute

    spec = importlib.util.spec_from_file_location("api_module", file_path)
    api_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api_module)

    endpoints = []

    if framework == "fastapi":
        app = getattr(api_module, "app", None)
        if app:
            for route in app.routes:
                if isinstance(route, APIRoute):
                    endpoints.append({
                        "api_name": route.name or "Unnamed API",
                        "path": route.path,
                        "methods": list(route.methods),
                        "parameters": [param.name for param in route.dependant.path_params]
                    })
    elif framework == "flask":
        app = getattr(api_module, "app", None)
        if app:
            for rule in app.url_map.iter_rules():
                endpoints.append({
                    "api_name": rule.endpoint,
                    "path": rule.rule,
                    "methods": list(rule.methods - {"HEAD", "OPTIONS"}),
                    "parameters": list(rule.arguments)
                })
    return endpoints

"""**Step 2:Initialize LangChain and LLM**"""

pip install -U langchain langchain-openai

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# Initialize the LLM
generation_llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=openai.api_key)

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["path", "methods", "parameters", "prompt"],
    template="{prompt}"
)

# Create the chain
generation_chain = LLMChain(
    llm=generation_llm,
    prompt=prompt_template
)

"""**Step 3: Generate Documentation for One API**"""

# Example endpoint details
example_endpoint = {
    "path": "/hello",
    "methods": ["GET"],
    "parameters": ["name"]
}

# Generate prompt for the endpoint
prompt = f"""
You are an expert API documentation specialist. Generate comprehensive API documentation for the following endpoint:
Path: {example_endpoint['path']}
Methods: {', '.join(example_endpoint['methods'])}
Parameters: {', '.join(example_endpoint['parameters']) if example_endpoint['parameters'] else 'None'}
"""

# Use the chain to generate documentation
response = generation_chain.run({
    "path": example_endpoint["path"],
    "methods": example_endpoint["methods"],
    "parameters": example_endpoint["parameters"],
    "prompt": prompt
})

# Print the documentation
print(response)

"""**Step 4: Process All APIs in the File**"""

def generate_api_documentation(api_file_path, framework):
    # Extract API details
    endpoints = extract_api_details(api_file_path, framework)

    # Store documentation for all endpoints
    documentation = []

    for endpoint in endpoints:
        # Generate prompt for the endpoint
        prompt = f"""
        You are an expert API documentation specialist. Generate comprehensive API documentation for the following endpoint:
        Path: {endpoint['path']}
        Methods: {', '.join(endpoint['methods'])}
        Parameters: {', '.join(endpoint['parameters']) if endpoint['parameters'] else 'None'}
        """

        # Use the chain to generate documentation
        result = generation_chain.run({
            "path": endpoint["path"],
            "methods": endpoint["methods"],
            "parameters": endpoint["parameters"],
            "prompt": prompt
        })

        # Save the result
        documentation.append({
            "path": endpoint["path"],
            "methods": endpoint["methods"],
            "parameters": endpoint["parameters"],
            "documentation": result
        })

        # Print documentation for review
        print(f"Documentation for {endpoint['path']}:\n{result}\n")

    return documentation

"""**step 5: save the doc to file**"""

def save_documentation_to_file(documentation, output_file_path):
    with open(output_file_path, "w") as f:
        for doc in documentation:
            f.write(f"# API Path: {doc['path']}\n")
            f.write(f"### Methods: {', '.join(doc['methods'])}\n")
            f.write(f"### Parameters: {', '.join(doc['parameters']) if doc['parameters'] else 'None'}\n")
            f.write(f"{doc['documentation']}\n\n")
    print(f"Documentation saved to {output_file_path}")

"""**step 6:run entire file**"""

# Path to the API file
api_file_path = "/content/drive/My Drive/297-project-api-documentation-generator/sample_apis.py"
framework = "fastapi"  # Set to "fastapi" or "flask" based on your project

# Generate documentation
documentation = generate_api_documentation(api_file_path, framework)

# Save to a Markdown file
output_file_path = "/content/drive/My Drive/297-project-api-documentation-generator/api_documentation_new.md"
save_documentation_to_file(documentation, output_file_path)
