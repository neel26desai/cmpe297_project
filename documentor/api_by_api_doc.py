from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import importlib.util
import os
import datetime
import json

class APIDocumentationGenerator:
    def __init__(self, model, api_file_path, output_dir, framework, prompt_version):
        self.api_file_path = api_file_path
        self.framework = framework
        self.prompt_version = prompt_version
        self.model = model
        self.now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Output file paths
        self.output_file_name = self.api_file_path.split("/")[-1].split(".")[0] + self.now
        self.output_directory = os.path.join(output_dir, self.model, "API-by-API", self.prompt_version)
        self.output_file_path = os.path.join(self.output_directory, self.output_file_name + ".md")
        
        # Prompt file
        self.prompt_file_path = "/Users/neel/Developer/cmpe297_project/prompts/bulk_api_prompts.json"  # Adjust path to your prompts
        
        # Initialize LLM
        self.llm = self.initialize_llm()

    def initialize_llm(self):
        return ChatOpenAI(model=self.model, temperature=0)

    def load_prompt_template(self):
        with open(self.prompt_file_path, "r") as file:
            prompts = json.load(file)
        return prompts.get(self.prompt_version, "Default prompt not found.")

    def extract_api_details(self):
        import importlib.util
        import inspect
        from fastapi.routing import APIRoute
        # Load the module
        spec = importlib.util.spec_from_file_location("api_module", self.api_file_path)
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        framework = self.framework

        endpoints = []

        if framework == "fastapi":
            app = getattr(api_module, "app", None)
            if app:
                for route in app.routes:
                    if isinstance(route, APIRoute):
                        # Extract handler function and its code
                        handler = route.endpoint
                        code = inspect.getsource(handler) if handler else "Code not found"

                        endpoints.append({
                            "api_name": route.name or "Unnamed API",
                            "path": route.path,
                            "methods": list(route.methods),
                            "parameters": [param.name for param in route.dependant.path_params],
                            "code": code
                        })
        elif framework == "flask":
            app = getattr(api_module, "app", None)
            if app:
                for rule in app.url_map.iter_rules():
                    # Extract handler function and its code
                    handler = app.view_functions.get(rule.endpoint)
                    code = inspect.getsource(handler) if handler else "Code not found"

                    endpoints.append({
                        "api_name": rule.endpoint,
                        "path": rule.rule,
                        "methods": list(rule.methods - {"HEAD", "OPTIONS"}),
                        "parameters": list(rule.arguments),
                        "code": code
                    })
        return endpoints

    def generate_api_documentation(self, endpoint):
        # Load prompt template
        prompt_template = self.load_prompt_template()
        
        # Format the prompt
        prompt = prompt_template.format(
            path=endpoint["path"],
            methods=", ".join(endpoint["methods"]),
            parameters=", ".join(endpoint["parameters"]) if endpoint["parameters"] else "None",
            code=endpoint["code"]
        )
        
        # Invoke the LLM to generate documentation
        response = self.llm.invoke(prompt)
        return response.content

    def save_documentation_to_file(self, documentation):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        with open(self.output_file_path, "w") as f:
            for doc in documentation:
                f.write(f"# API Path: {doc['path']}\n")
                f.write(f"### Methods: {', '.join(doc['methods'])}\n")
                f.write(f"### Parameters: {', '.join(doc['parameters']) if doc['parameters'] else 'None'}\n")
                f.write(f"{doc['documentation']}\n\n")
        print(f"API Documentation saved to {self.output_file_path}")

    def process_and_generate_documentation(self):
        # Extract API details
        endpoints = self.extract_api_details()
        
        # Generate documentation for each API
        documentation = []
        for endpoint in endpoints:
            print(f"Processing {endpoint['path']}...")
            doc_content = self.generate_api_documentation(endpoint)
            documentation.append({
                "path": endpoint["path"],
                "methods": endpoint["methods"],
                "parameters": endpoint["parameters"],
                "documentation": doc_content
            })
            print(f"Documentation generated for {endpoint['path']}\n")
        
        # Save all documentation to a file
        self.save_documentation_to_file(documentation)
