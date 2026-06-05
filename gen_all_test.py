
import ast
import json
import pandas as pd
import os
import subprocess
subprocess.run([
    "git",
    "clone",
    "https://github.com/django/django",
    "django_repo"
])
TARGET_DIR = './django_repo/tests/'

class TestParser(ast.NodeVisitor):
    def __init__(self):
        self.tests = []
        self.current_class = None

    def visit_ClassDef(self, node):
        # Save class name containing 'Test' 
        if node.name.startswith('Test') or 'Test' in node.name:
            self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):

        # Just focus on functions that look like 'test_'
        if node.name.startswith('test_'):
            # Get the source code of the test.
            try:
                code_context = ast.unparse(node)
            except:
                code_context = "Source code extraction needs Python 3.9+"
            
            # Analyze which functions this function calls. (Static Call Graph)
            called_functions = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        called_functions.append(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        called_functions.append(child.func.attr)
            
            self.tests.append({
                'test_class': self.current_class,
                'test_name': node.name,
                'called_functions': list(set(called_functions)), # Basic Node Coverage
                'code_context': code_context
            })
        self.generic_visit(node)

# function to perform a full directory and group scan.
def parse_all_tests(directory):
    all_tests = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    tree = ast.parse(source)
                    parser = TestParser()
                    parser.visit(tree)
                    
                    # Add file information to the result
                    for t in parser.tests:
                        t['file_path'] = file_path
                    all_tests.extend(parser.tests)
                except Exception as e:
                    print(f"Error reading file! {file_path}: {e}")
    return all_tests

# 1. Scan the entire test directory
parsed_data = parse_all_tests(TARGET_DIR)
# 2. Convert to DataFrame
df_tests = pd.DataFrame(parsed_data)
print(f"Found {len(df_tests)} test cases.")
# 3. Group all data
# Idea: Group test cases that are in the same Test Class (or the same file) into a single group
grouped_tests = df_tests.groupby('test_class')

all_grouped_data = {}
for class_name, group in grouped_tests:
    if class_name: # Skip test cases that are not in any class
        # Only take classes that have 2 or more test cases (since 1 test case cannot have duplicates)
        if len(group) > 1:
            all_grouped_data[class_name] = group.to_dict(orient='records')

# Export all grouped data to JSON
with open('all_grouped_tests.json', 'w', encoding='utf-8') as f:
    json.dump(all_grouped_data, f, ensure_ascii=False, indent=2)

print(f"Filtered {len(all_grouped_data)} groups (Test Class) that may contain duplicate tests.")
print("Data saved to 'all_grouped_tests.json'.")