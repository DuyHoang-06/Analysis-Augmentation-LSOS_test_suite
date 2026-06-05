import json
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open('all_grouped_tests.json', 'r', encoding='utf-8') as f:
    all_groups = json.load(f)

# Similarity Threshold: 0.90 (Similarities of 90% or more will be considered duplication.)
SIMILARITY_THRESHOLD = 0.90 

duplicates_report = []
total_saved_tests = 0

print("Starting duplicate detection tool using Cosine Similarity...\n")

# Scan each group (Test Class)
for class_name, test_cases in all_groups.items():
    if len(test_cases) < 2:
        continue # Skip groups with only 1 test
        
    # Get test name list and code content
    test_names = [tc['test_name'] for tc in test_cases]
    test_codes = [tc['code_context'] for tc in test_cases]
    
    try:
        # encode code into Vector
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(test_codes)
        
        # Calculate the similarity matrix (all tests are cross-compared with each other)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find pairs of tests that have a similarity exceeding the threshold.
        found_duplicates_in_group = set()
        
        for i in range(len(test_names)):
            for j in range(i + 1, len(test_names)): # Only compare the upper half of the matrix to avoid duplicates
                score = similarity_matrix[i][j]
                
                if score >= SIMILARITY_THRESHOLD:
                    # Record duplicate pairs
                    duplicates_report.append({
                        "test_class": class_name,
                        "test_1": test_names[i],
                        "test_2": test_names[j],
                        "similarity_score": round(score * 100, 2)
                    })
                    found_duplicates_in_group.add(test_names[j]) # Mark the second test as a duplicate
                    
        total_saved_tests += len(found_duplicates_in_group)
        
    except Exception as e: 
        pass

print(f"Found {len(duplicates_report)} pairs of tests that may be duplicates.")
print(f"If grouped, at least {total_saved_tests} test cases can be saved.\n")

print("--- TOP 5 most SIMILAR TEST PAIRS ---")
duplicates_report.sort(key=lambda x: x['similarity_score'], reverse=True)

for dup in duplicates_report[:5]:
    print(f"Class: {dup['test_class']}")
    print(f"  - {dup['test_1']}")
    print(f"  - {dup['test_2']}")
    print(f"  => Similarity: {dup['similarity_score']}%\n")

with open('duplicate_suspects_report.json', 'w', encoding='utf-8') as f:
    json.dump(duplicates_report, f, ensure_ascii=False, indent=2)
print("Details saved to 'duplicate_suspects_report.json'.")