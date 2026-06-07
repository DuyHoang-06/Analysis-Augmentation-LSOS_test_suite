import ast
import json
import networkx as nx
import matplotlib.pyplot as plt

SOURCE_FILE = './django_repo/django/contrib/auth/views.py' # File contains main logic of the system
TEST_FILE = './django_repo/tests/auth_tests/test_views.py' # File contains tests

G = nx.DiGraph()

def get_source_functions(filepath):
    """Scan source code to find all system functions that have been written"""
    funcs = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                # Get regular functions, skipping built-in functions (starting with __)
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('__'):
                    funcs.add(node.name)
    except Exception as e:
        print(f"Error reading source file: {e}")
    return funcs

source_functions = get_source_functions(SOURCE_FILE)

# Build call graph from test code
class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.current_test_func = None

    def visit_FunctionDef(self, node):
        # Only focus on test functions
        if node.name.startswith('test_'):
            self.current_test_func = node.name
            # Add node (Vertex) for the test function, color it blue
            G.add_node(node.name, color='lightblue', type='test')
            self.generic_visit(node)
        self.current_test_func = None

    def visit_Call(self, node):
        if self.current_test_func:
            callee = None
            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee = node.func.attr
            
            if callee:
                # Add node for the called function (System function), color it orange
                if not G.has_node(callee):
                    G.add_node(callee, color='orange', type='system')
                # DRAW EDGES from Test function -> System function
                G.add_edge(self.current_test_func, callee)
                
        self.generic_visit(node)

print("Building Call Graph...")
try:
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
        builder = CallGraphBuilder()
        builder.visit(tree)
except Exception as e:
    print(f"Error reading test file: {e}")


# Calculate Coverage Gaps
# Get all "orange nodes" (system functions that have been called by tests)
called_in_test = {n for n, attr in G.nodes(data=True) if attr.get('type') == 'system'}

# Intersection of 2 sets: functions that are in the source AND called by tests
covered_funcs = source_functions.intersection(called_in_test)

# Difference of 2 sets: Functions that are in the source BUT never called by tests
gaps = source_functions.difference(called_in_test)

coverage_percent = (len(covered_funcs) / len(source_functions)) * 100 if source_functions else 0

print("\n--- REPORT ON COVERAGE GAPS ---")
print(f" - Total number of functions in the system: {len(source_functions)}")
print(f" - Number of functions tested (Touched): {len(covered_funcs)}")
print(f" - COVERAGE (Node Coverage): {coverage_percent:.2f}%")

print(f"\nDETECTED {len(gaps)} COVERAGE GAPS:")
for gap in gaps:
    print(f"   [!] {gap}")

report_data = {
    "module": SOURCE_FILE,
    "node_coverage_percent": round(coverage_percent, 2),
    "total_gaps": len(gaps),
    "untested_functions": list(gaps)
}
with open('coverage_gaps_report.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)
print("\nSaved coverage gaps list to file: 'coverage_gaps_report.json'")

print(f"\nDrawing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges...")

plt.figure(figsize=(20, 20))
colors = [node[1]['color'] if 'color' in node[1] else 'gray' for node in G.nodes(data=True)]
pos = nx.spring_layout(G, k=3.0, iterations=450, seed=42)

nx.draw(G, pos, with_labels=True, node_color=colors, 
        node_size=2000, font_size=8, font_weight='bold', 
        arrows=True, arrowsize=15, edge_color='gray')

plt.title(f"Test-to-Code Call Graph | Coverage: {coverage_percent:.2f}%", size=15)
plt.savefig("call_graph_mapping.png", format="PNG", dpi=300)
plt.close()

print("Saved graph to file: 'call_graph_mapping.png'")