from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import importlib.util
import json
import os 
import datetime

class BulkAPIDocumentationGenerator:
    def __init__(self, model,api_file_path, output_dir, prompt_version):
        self.api_file_path = api_file_path
        self.model = model
        self.prompt_version = prompt_version
        self.now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")#gets the current date and time
        self.output_file_name =self.api_file_path.split("/")[-1].split(".")[0]+self.now#gets the name of the file you are testing
        #directotry to save the results, will be the model name
        self.output_directory = os.path.join(output_dir,self.model,"BatchAPI",self.prompt_version)
        self.output_file_path = os.path.join(self.output_directory,self.output_file_name+".md")
        
        self.prompt_file_path = "/Users/neel/Developer/cmpe297_project/prompts/bulk_api_prompts.json"
        self.model = model
        self.llm = self.initialize_llm()

    def initialize_llm(self):
        return ChatOpenAI(model="gpt-4", temperature=0)

    def load_prompt_template(self):
        with open(self.prompt_file_path, "r") as file:
            prompts = json.load(file)
        return prompts.get(self.prompt_version, "Default prompt not found.")

    def extract_api_file_content(self):
        with open(self.api_file_path, "r") as file:
            return file.read()

    def generate_readme(self):
        api_file_content = self.extract_api_file_content()
        prompt_template = self.load_prompt_template()

        prompt = prompt_template.format(api_file_content=api_file_content)

        response = self.llm.invoke(prompt)
        return response.content
    
    def save_readme_to_file(self, documentation):
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        with open(self.output_file_path, "w") as f:
            f.write(documentation)
        print(f"README saved to {self.output_file_path}")
    
    def process_and_generate_documentation(self):
        # Generate README
        readme_content = self.generate_readme()
        # Save README to file
        self.save_readme_to_file(readme_content)


if __name__ == "__main__":
    # Paths and prompt version
    api_file_path = "/Users/neel/Developer/cmpe297_project/sample_inputs/sample_apis.py"
    output_file_path = "/Users/neel/Developer/cmpe297_project/output_docs"
    prompt_version = "v1"  # Specify the prompt version
    model = "gpt-4o-mini"

    generator = BulkAPIDocumentationGenerator(model, api_file_path, output_file_path, prompt_version)

    # Process and generate documentation
    generator.process_and_generate_documentation()
