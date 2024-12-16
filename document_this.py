import argparse
from documentor.bulk_api_doc import BulkAPIDocumentationGenerator

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Generate API documentation using LLMs.")

    # Adding argument for bulk mode or API-by-API
    parser.add_argument(
        '-m', '--mode',
        type=str,
        default='bulk',
        help='Mode of documentation generation. Options: bulk, api_by_api (default: bulk).'
    )
    # Add arguments
    parser.add_argument(
        '-a', '--api_file_path',
        default="/Users/neel/Developer/cmpe297_project/sample_inputs/sample_apis.py",
        help="Path to the API file to be documented (default: /Users/neel/Developer/cmpe297_project/sample_inputs/sample_apis.py)."
    )
    parser.add_argument(
        '-o', '--output_dir',
        default="/Users/neel/Developer/cmpe297_project/output_docs",
        help="Directory where the generated README file will be saved (default: /Users/neel/Developer/cmpe297_project/output_docs)."
    )
    parser.add_argument(
        '-md', '--model',
        default="gpt-4o-mini",
        help="LLM model to use for generating documentation (default: gpt-4o-mini)."
    )
    parser.add_argument(
        '-p', '--prompt_version',
        default="v1",
        help="Version of the prompt to use from the prompt file (default: v1)."
    )

    # Parse the arguments
    args = parser.parse_args()

    if args.mode == 'bulk':
        # Instantiate the documentation generator
        generator = BulkAPIDocumentationGenerator(
            model=args.model,
            api_file_path=args.api_file_path,
            output_dir=args.output_dir,
            prompt_version=args.prompt_version
        )

        # Process and generate documentation
        generator.process_and_generate_documentation()

if __name__ == "__main__":
    main()
