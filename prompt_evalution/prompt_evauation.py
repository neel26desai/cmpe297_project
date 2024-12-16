from langchain.schema.runnable import RunnableSequence
import json
import logging
import sys
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(message)s")

# Load prompts
def load_prompts(prompts_path):
    with open(prompts_path, 'r') as prompts_file:
        return json.load(prompts_file)

# Extract API details
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

# Generate and evaluate

def generate_and_evaluate(prompts, apis, generation_llm, evaluation_llm, output_file="results.json"):
    from statistics import mean

    # Initialize chains
    generation_chain = RunnableSequence(
        PromptTemplate(
            input_variables=["path", "methods", "", "prompt"],
            template="{prompt}parameters"
        ), 
        generation_llm
    )
    evaluation_chain = RunnableSequence(
        PromptTemplate(
            input_variables=["response"],
            template="""
            You are an API documentation quality expert. Your task is to critically evaluate the quality of the documentation generated for an API endpoint. Imagine you are a new developer or user with no prior knowledge of the system, relying solely on this documentation for understanding and implementation. Assess the response stringently based on the following criteria and provide scores for each:
            1. **Completeness**: Does the documentation address all aspects of the endpoint, including its purpose, functionality, methods, parameters, outputs, and potential errors? Ensure it covers all details required to confidently use the endpoint without additional clarification. (Score: 1-10)
            2. **Clarity**: Is the documentation written in clear, concise, and simple language that can be easily understood by someone unfamiliar with the system? Avoid vague, ambiguous, or overly technical explanations. (Score: 1-10)
            3. **Accuracy**: Does the documentation precisely describe the endpoint's behavior and intended functionality without errors, omissions, or contradictions? (Score: 1-10)
            4. **Relevance**: Is the documentation focused only on the endpoint's purpose, avoiding unnecessary or confusing details? Ensure it directly answers the user's potential questions. (Score: 1-10)
            5. **Professional Tone and Format**: Is the documentation written in a professional and instructional tone, following best practices in formatting, structure, and conventions for API documentation? (Score: 1-10)

            Provide your response in the following format:
            `Completeness:<score>, Clarity:<score>, Accuracy:<score>, Relevance:<score>, Professional Tone and Format:<score>, Overall:<overall_score>`

            Additionally:
            - Assign an **Overall Score** (average of all the criteria rounded to the nearest whole number).
            - If any score is less than 6, briefly explain the shortcomings in that area to highlight where the documentation failed to meet expectations.

            Ensure that your evaluation is very stringent, reflecting the perspective of a developer or user who relies solely on the documentation to fully understand and confidently use the API.
            Response:
            {response}
            """
        ), 
        evaluation_llm
    )

    scores = {}
    results = {}

    for api in apis[:2]:
        path = api['path']
        methods = api['methods']
        parameters = api['parameters']

        for version, prompt_template in prompts.items():
            # Fill the prompt
            filled_prompt = prompt_template.format(path=path, methods=methods, parameters=parameters)
            
            # Generate response
            response = generation_chain.invoke({"path": path, "methods": methods, "parameters": parameters, "prompt": filled_prompt})
            
            # Evaluate response
            evaluation = evaluation_chain.invoke({"response": response}).content
            logging.info(f"Version: {version}, API: {path},\nEvaluation: {evaluation}")

            # Parse evaluation for scores
            try:
                evaluation_scores = {criterion.split(":")[0].strip(): int(criterion.split(":")[1].strip())
                                     for criterion in evaluation.split(",")}
                overall_score = evaluation_scores.get("Overall", 0)
            except (ValueError, IndexError):
                logging.error(f"Failed to parse scores for API: {path} with version: {version}")
                overall_score = 0

            # Accumulate scores
            scores[version] = scores.get(version, 0) + overall_score

            # Save results
            results[f"{version}_{path}"] = {
                "path": path,
                "methods": methods,
                "parameters": parameters,
                "response": response,
                "evaluation": evaluation,
                "overall_score": overall_score
            }

    # # Save results to a JSON file
    # with open(output_file, "w") as file:
    #     json.dump(results, file, indent=4)

    # print(f"Results saved to {os.path.abspath(output_file)}")

    return results, scores

def parse_results(results):
    parsed_results = {}
    for key, value in results.items():
        #check the the first 2 characters of the key are the version number
        version = key[:2]
        #check if the version number is in the dictionary
        if version not in results:
            parsed_results[version] = {}
        #now we look at evaluation part
        eval = results[key]['evaluation']
        #split the evaluation by comma, first 5 elements are the criteria scores
        individual_evals = eval.split(",")[:5]
        #split the individual evaluation by colon
        for individual_eval in individual_evals:
            #split the individual evaluation by colon
            print(individual_eval)
            criterion, score = individual_eval.split(":")
            #add the criterion and score to the dictionary
            parsed_results[version][criterion.strip()] = int(score)
    return parsed_results


if __name__=="__main__":
    # Set up LLMs
    generation_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    evaluation_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # File paths and framework
    prompts_file = "prompts.json"
    api_file = "/Users/neel/Developer/cmpe297_project/complex_api.py"
    framework = "fastapi"

    # Load prompts and extract APIs
    prompts = load_prompts(prompts_file)
    #give options to remove prompt versions
    prompts.pop('v1')
    apis = extract_api_details(api_file, framework)

    # Run the pipeline
    results, scores = generate_and_evaluate(prompts, apis, generation_llm, evaluation_llm)
    results_temp = parse_results(results)
    #save the results to a json file
    with open("results.json", "w") as file:
        json.dump(results_temp, file, indent=4)
