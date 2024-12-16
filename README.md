# cmpe297_project

Before running make sure to set `export OPENAI_API_KEY=<YOUR_API_KEY>`


# How to use api_doc_gen_using_langhchain.py file 

1. Clone the Repository
2. Install Requirements:

```
pip install -r requirements.txt
```

3. Create .env file dynamically in Colab
```
with open('.env', 'w') as f:
f.write("OPENAI_API_KEY=your_api_key")
```
# CLI Tool for Generating API Documentation

This CLI tool allows you to generate API documentation using an LLM (Large Language Model) like GPT. It supports two modes of operation: `bulk` (generates documentation for the entire API file at once) and `api_by_api` (handles documentation one API endpoint at a time).

---

## Prerequisites

1. Python 3.8 or higher installed on your system.
2. Required Python libraries installed:
   - `argparse`
   - The `documentor.bulk_api_documentation_generator` module (ensure it is accessible).

---

## Usage

### Basic Command Structure

```bash
python document_this.py [OPTIONS]
```

### Options

| Short Form | Full Option Name     | Description                                                                                       | Default Value                                                             |
|------------|----------------------|---------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `-m`       | `--mode`             | Mode of documentation generation. Options: `bulk`, `api_by_api`.                                  | `bulk`                                                                    |
| `-a`       | `--api_file_path`    | Path to the API file to be documented.                                                            | `/Users/neel/Developer/cmpe297_project/sample_inputs/sample_apis.py`      |
| `-o`       | `--output_dir`       | Directory where the generated README file will be saved.                                          | `/Users/neel/Developer/cmpe297_project/output_docs`                       |
| `-md`      | `--model`            | LLM model to use for generating documentation.                                                    | `gpt-4o-mini`                                                             |
| `-p`       | `--prompt_version`   | Version of the prompt to use from the prompt file.                                                | `v1`                                                                      |

---

### Examples

#### 1. Bulk Mode (Default)

Generate documentation for the entire API file in bulk:

```bash
python cli_tool.py -m bulk -a /path/to/api_file.py -o /path/to/output_dir -md gpt-4o-mini -p v1
```

If no options are provided, the tool uses the default values:

```bash
python cli_tool.py
```

#### 2. API-by-API Mode

Generate documentation for individual endpoints:

```bash
python cli_tool.py -m api_by_api -a /path/to/api_file.py -o /path/to/output_dir -md gpt-4o-mini -p v1
```

---

## Additional Notes

- **Custom Prompts:** Ensure that the `bulk_api_prompts.json` file includes the required prompts for the specified `--prompt_version`. Otherwise, an error will be raised.
- **Output:** The README file is saved in the specified output directory, organized under `BatchAPI` with the API file name as the folder name.

---

## Error Handling

- If an invalid mode is passed, the script will print:
  ```text
  Invalid mode: <mode>. Use 'bulk' or 'api_by_api'.
  ```
- Ensure that the API file path and output directory are accessible; otherwise, errors may occur during file operations.

---

