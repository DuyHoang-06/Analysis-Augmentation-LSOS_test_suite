import subprocess
import time

print("\n" + "="*60)
print("   Launching test pipeline experiment benchmark")
print("="*60)

# AST Extraction
print("\n[Executing] Stage 1: Scanning repository and AST extraction...")
start_ast = time.time()
subprocess.run(["python", "gen_all_test.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
duration_ast = time.time() - start_ast
print(f"--> Stage 1 completed in: {duration_ast:.4f} seconds")

# NLP Similarity
print("\n[Executing] Stage 2: Processing NLP semantic similarity...")
start_nlp = time.time()
subprocess.run(["python", "gen_duplicate.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
duration_nlp = time.time() - start_nlp
print(f"--> Stage 2 completed in: {duration_nlp:.4f} seconds")

# Call Graph and Gap Analysis
print("\n[Executing] Stage 3: Constructing global call graph and detecting gaps...")
start_graph = time.time()
subprocess.run(["python", "coverage_gap_analysis.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
duration_graph = time.time() - start_graph
print(f"--> Stage 3 completed in: {duration_graph:.4f} seconds")

# Component Graphs
print("\n[Executing] Component stage: Rendering individual test class graphs...")
start_build = time.time()
subprocess.run(["python", "build_all_graph.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
duration_build = time.time() - start_build
print(f"--> Component rendering completed in: {duration_build:.4f} seconds")

# Final experimental summary
total_local_pipeline = duration_ast + duration_nlp + duration_graph
print("\n" + "="*60)
print("   Experimental time benchmark summary")
print("="*60)
print(f" - Stage 1 (AST parsing)        : {duration_ast:.4f} seconds")
print(f" - Stage 2 (NLP deduplication)  : {duration_nlp:.4f} seconds")
print(f" - Stage 3 (Call graph gaps)    : {duration_graph:.4f} seconds")
print(f" - Component image rendering     : {duration_build:.4f} seconds")
print("-"*60)
print(f"   Total local pipeline latency : {total_local_pipeline:.4f} seconds")
print("="*60 + "\n")