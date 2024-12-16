# cmpe297_project

Before running make sure to set `export OPENAI_API_KEY=<YOUR_API_KEY>`


#How to use api_doc_gen_using_langhchain.py file 

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
4. Run the script
   
 ```
  !python api_doc_gen_using_langchain.py --api_file_path sample_apis.py --output_markdown_path output_docs/api_docs.md
```
5. Verify the Output
Check if the Markdown file is created successfully:

```
!cat output_docs/api_docs.md
```

--------------------------------------------------------------------------------------------------------------

# Output

The generated documentation is saved to your specified path
```
output_docs/api_docs.md

```
