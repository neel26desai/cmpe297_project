import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import os
import re
import argparse
from langchain_openai import ChatOpenAI
from documentor.api_by_api_doc import APIDocumentationGenerator
from datetime import datetime

class MultiVersionEvaluator:
    def __init__(self, model, api_file_path, generated_docs, prompt_versions, output_dir):
        """
        :param model: LLM model name
        :param api_file_path: Path to the original API file
        :param generated_docs: Dictionary of {prompt_version: generated_readme_content}
        :param prompt_versions: List of prompt versions to evaluate
        :param output_dir: Directory to save evaluation results
        """
        self.model = model
        self.api_file_path = api_file_path
        self.generated_docs = generated_docs  # {version: readme_content}
        self.prompt_versions = prompt_versions
        self.output_dir = os.path.join(output_dir, "critic_evaluations")
        os.makedirs(self.output_dir, exist_ok=True)
        self.llm = self.initialize_llm()

    def initialize_llm(self):
        return ChatOpenAI(model=self.model, temperature=0)

    def load_api_file_content(self):
        with open(self.api_file_path, "r") as file:
            return file.read()

    def evaluate_single_version(self, version, readme_content):
        # Static evaluation prompt
        evaluation_prompt = """
        You are a meticulous technical documentation reviewer tasked with evaluating API documentation. 
        Evaluate the following generated README documentation based on the criteria listed below:

        **Evaluation Criteria:**
        1. **Completeness:** Does the README include all key sections (Overview, Endpoints, Methods, Parameters, Examples)? Provide a score (1-10) and justify your score.
        2. **Clarity:** Is the README clear, well-structured, and easy to understand? Provide a score (1-10) and justify your score.
        3. **Accuracy:** Does the documentation accurately represent the API file content? Provide a score (1-10) and justify your score.
        4. **Relevance:** Is the documentation relevant and helpful to both technical and non-technical users? Provide a score (1-10) and justify your score.

        **Input API File Content:**
        {api_file_content}

        **Generated README:**
        {generated_readme}

        Provide scores and justification for each criterion. Conclude with an overall score (average of the four criteria) and brief feedback on areas of improvement.
        """

        # Load API file content
        api_file_content = self.load_api_file_content()

        # Format the prompt with API content and README content
        formatted_prompt = evaluation_prompt.format(
            api_file_content=api_file_content,
            generated_readme=readme_content
        )

        # LLM evaluation
        print(f"Evaluating prompt version: {version}")
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def parse_scores(self, evaluation_response):
        """
        Extract scores for completeness, clarity, accuracy, and relevance from LLM response.
        """
        scores = {}
        patterns = {
            "completeness": r"Completeness:\s*(\d+)/10",
            "clarity": r"Clarity:\s*(\d+)/10",
            "accuracy": r"Accuracy:\s*(\d+)/10",
            "relevance": r"Relevance:\s*(\d+)/10"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, evaluation_response, re.IGNORECASE)
            if match:
                scores[key] = int(match.group(1))
            else:
                scores[key] = None  # Set to None if the score isn't found
        return scores

    def check_existing_response(self, version):
        """
        Check if an evaluation file already exists for the given version.
        """
        output_file = os.path.join(self.output_dir, f"evaluation_{version}.json")
        if os.path.exists(output_file):
            return output_file
        return None

    def evaluate_all_versions(self):
        # Evaluate all versions and store results
        evaluation_results = {}
        for version, readme_content in self.generated_docs.items():
            existing_file = self.check_existing_response(version)
            if existing_file:
                choice = input(f"Evaluation for version '{version}' already exists. Reuse it? (y/n): ").strip().lower()
                if choice == "y":
                    print(f"Reusing existing evaluation for version '{version}'...")
                    with open(existing_file, "r") as f:
                        evaluation_data = json.load(f)
                        scores = evaluation_data["scores"]
                else:
                    print(f"Generating new evaluation for version '{version}'...")
                    result = self.evaluate_single_version(version, readme_content)
                    scores = self.parse_scores(result)
                    self.save_evaluation(version, scores, result)
            else:
                print(f"Generating evaluation for version '{version}'...")
                result = self.evaluate_single_version(version, readme_content)
                scores = self.parse_scores(result)
                self.save_evaluation(version, scores, result)

            evaluation_results[version] = scores
        return evaluation_results

    def save_evaluation(self, version, scores, raw_response):
        # Generate a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Append timestamp to the filename
        output_file = os.path.join(self.output_dir, f"evaluation_{version}_{timestamp}.json")
        
        # Save structured scores and raw LLM response to JSON
        evaluation_data = {
            "version": version,
            "timestamp": timestamp,
            "scores": scores,
            "raw_response": raw_response
        }
        with open(output_file, "w") as f:
            json.dump(evaluation_data, f, indent=4)
        
        print(f"Evaluation saved: {output_file}")

    def evaluate_single_version(self, version, readme_content):
        # Static evaluation prompt
        evaluation_prompt = """
        You are a meticulous technical documentation reviewer tasked with evaluating API documentation. 
        Evaluate the following generated README documentation based on the criteria listed below:

        **Evaluation Criteria:**
        1. **Completeness:** Does the README include all key sections (Overview, Endpoints, Methods, Parameters, Examples)? Provide a score (1-10) and justify your score.
        2. **Clarity:** Is the README clear, well-structured, and easy to understand? Provide a score (1-10) and justify your score.
        3. **Accuracy:** Does the documentation accurately represent the API file content? Provide a score (1-10) and justify your score.
        4. **Relevance:** Is the documentation relevant and helpful to both technical and non-technical users? Provide a score (1-10) and justify your score.

        **Input API File Content:**
        {api_file_content}

        **Generated README:**
        {generated_readme}

        Provide scores and justification for each criterion. Conclude with an overall score (average of the four criteria) and brief feedback on areas of improvement.
        """

        # Load API file content
        api_file_content = self.load_api_file_content()

        # Format the prompt with API content and README content
        formatted_prompt = evaluation_prompt.format(
            api_file_content=api_file_content,
            generated_readme=readme_content
        )

        # LLM evaluation
        print(f"Evaluating prompt version: {version}")
        response = self.llm.invoke(formatted_prompt)
        return response.content


    def summarize_results(self, evaluation_results):
        # Print and summarize evaluation feedback
        print("\n=== Summary of Evaluations ===")
        for version, scores in evaluation_results.items():
            print(f"\nPrompt Version: {version}")
            print(f"Scores: {scores}")
        print("\nEvaluation Complete. Check the output directory for details.")


def get_latest_file(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    return max(files, key=os.path.getctime)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for evaluating API documentation with LLMs.")
    parser.add_argument(
        "--api_file", 
        type=str, 
        default="/Users/neel/Developer/cmpe297_project/sample_inputs/sample_apis.py", 
        help="Path to the input API file."
    )
    parser.add_argument(
        "--regenerate_file", 
        action="store_true", 
        help="Regenerate documentation files."
    )
    args = parser.parse_args()

    # Input parameters
    api_file_path = args.api_file  # Set from CLI argument
    output_dir = "/Users/neel/Developer/cmpe297_project/output_docs"
    model = "gpt-4o-mini"
    prompt_versions = ["v1", "v2"]
    generated_docs = {}

    if args.regenerate_file:
        for version in prompt_versions:
            print(f"Generating documentation for version: {version}")
            generator = APIDocumentationGenerator(model=model, api_file_path=api_file_path, output_dir=output_dir, prompt_version=version,framework="fastapi")
            generator.process_and_generate_documentation()
            with open(generator.output_file_path, "r") as f:
                generated_docs[version] = f.read()
    else:
        for version in prompt_versions:
            saved_dir = f"{output_dir}/{model}/API-by-API/{version}"
            latest_file = get_latest_file(saved_dir)
            with open(latest_file, "r") as f:
                generated_docs[version] = f.read()

    evaluator = MultiVersionEvaluator(model, api_file_path, generated_docs, prompt_versions, output_dir)
    results = evaluator.evaluate_all_versions()
    evaluator.summarize_results(results)
