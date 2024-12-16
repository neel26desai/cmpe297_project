from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import importlib.util
from fastapi.routing import APIRoute

class APIDocumentationGenerator:
    def __init__(self,model ,api_file_path, framework, output_file_path):
        self.api_file_path = api_file_path
        self.framework = framework
        self.output_file_path = output_file_path
        self.model = model
        self.llm = self.initialize_llm(self.model)
        self.generation_chain = self.create_generation_chain()

    def initialize_llm(self,model="gpt-4o-mini"):
        return ChatOpenAI(model=model, temperature=0)

    def create_generation_chain(self):
        prompt_template = PromptTemplate(
            input_variables=["path", "methods", "parameters", "prompt"],
            template="{prompt}"
        )
        return LLMChain(
            llm=self.llm,
            prompt=prompt_template
        )

    def extract_api_details(self):
        spec = importlib.util.spec_from_file_location("api_module", self.api_file_path)
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)

        endpoints = []

        if self.framework == "fastapi":
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
        elif self.framework == "flask":
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

    def generate_api_documentation_single(self, example_endpoint):
        prompt = f"""
        You are an expert API documentation specialist. Generate comprehensive API documentation for the following endpoint:
        Path: {example_endpoint['path']}
        Methods: {', '.join(example_endpoint['methods'])}
        Parameters: {', '.join(example_endpoint['parameters']) if example_endpoint['parameters'] else 'None'}
        """

        response = self.generation_chain.run({
            "path": example_endpoint["path"],
            "methods": example_endpoint["methods"],
            "parameters": example_endpoint["parameters"],
            "prompt": prompt
        })

        return response

    def generate_api_documentation(self):
        endpoints = self.extract_api_details()
        documentation = []

        for endpoint in endpoints:
            prompt = f"""
            You are an expert API documentation specialist. Generate comprehensive API documentation for the following endpoint:
            Path: {endpoint['path']}
            Methods: {', '.join(endpoint['methods'])}
            Parameters: {', '.join(endpoint['parameters']) if endpoint['parameters'] else 'None'}
            """

            result = self.generation_chain.run({
                "path": endpoint["path"],
                "methods": endpoint["methods"],
                "parameters": endpoint["parameters"],
                "prompt": prompt
            })

            documentation.append({
                "path": endpoint["path"],
                "methods": endpoint["methods"],
                "parameters": endpoint["parameters"],
                "documentation": result
            })

            print(f"Documentation for {endpoint['path']}:\n{result}\n")

        return documentation

    def save_documentation_to_file(self, documentation):
        with open(self.output_file_path, "w") as f:
            for doc in documentation:
                f.write(f"# API Path: {doc['path']}\n")
                f.write(f"### Methods: {', '.join(doc['methods'])}\n")
                f.write(f"### Parameters: {', '.join(doc['parameters']) if doc['parameters'] else 'None'}\n")
                f.write(f"{doc['documentation']}\n\n")
        print(f"Documentation saved to {self.output_file_path}")
    
    


def generate_doc_api_by_api(api_file_path, framework, output_file_path):
    # Paths and framework

    generator = APIDocumentationGenerator(api_file_path, framework, output_file_path)

    # Generate documentation
    documentation = generator.generate_api_documentation()


    # Save to a Markdown file
    generator.save_documentation_to_file(documentation)

if __name__ == "__main__":
    # Paths and framework
    api_file_path = "/Users/neel/Developer/cmpe297_project/complex_api.py"
    output_file_path = "output_docs/content/output_docs/api_docs.md"
    framework = "fastapi"  # Set to "fastapi" or "flask" based on your project
    generate_doc_api_by_api(api_file_path, framework, output_file_path)