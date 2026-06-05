import json
import time
import os
from openai import OpenAI

print("🔥 FILE RUNNING")

# ====== CONFIG API ======
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # GET YOUR API KEY

# ====== LOAD FILE ======
try:
    with open('duplicate_suspects_report.json', 'r', encoding='utf-8') as f:
        duplicate_list = json.load(f)

    with open('all_grouped_tests.json', 'r', encoding='utf-8') as f:
        all_code_data = json.load(f)

except Exception as e:
    print("❌ Error reading file:", e)
    exit()

print(f"✅ Number of duplicate pairs: {len(duplicate_list)}")
print(f"✅ Number of classes: {len(all_code_data)}")

refactored_results = []

print("\n🚀 Starting processing...\n")

# ====== MAIN LOOP ======
for i, item in enumerate(duplicate_list):
    try:
        class_name = item['test_class']
        t1_name = item['test_1']
        t2_name = item['test_2']

        print(f"[{i+1}] Processing: {class_name} | {t1_name} & {t2_name}")

        class_tests = all_code_data.get(class_name, [])

        code_1 = next(
            (tc['code_context'] for tc in class_tests if tc['test_name'] == t1_name),
            None
        )

        code_2 = next(
            (tc['code_context'] for tc in class_tests if tc['test_name'] == t2_name),
            None
        )

        if not code_1 or not code_2:
            print(f"❌ Could not find code for {t1_name} or {t2_name}")
            continue

        # ====== PROMPT ======
        full_prompt = f"""
You are a QA Automation Engineer specializing in Python + Django.

The following are 2 tests in class {class_name} that are similar with a similarity score of {item['similarity_score']}%.

Please:
- Combine them into a single test

Please:
- Combine them into a single test
- Use self.subTest()
- Keep the logic complete

Only return:
1. Complete Python code
2. one short line explanation

Test 1:
{code_1}

Test 2:
{code_2}
"""

        # ====== CALL OPENAI ======
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3
        )

        new_code = response.choices[0].message.content

        refactored_results.append({
            "class": class_name,
            "original_tests": [t1_name, t2_name],
            "refactored_code": new_code
        })

        print(f"✅ Done: {t1_name} & {t2_name}")

        time.sleep(2)

    except Exception as e:
        print(f"❌ Error at pair {i}: {e}")
        continue

# ====== SAVE FILE ======
try:
    with open('final_refactored_tests.json', 'w', encoding='utf-8') as f:
        json.dump(refactored_results, f, ensure_ascii=False, indent=2)

    print("\n🎉 Done! Saved to final_refactored_tests.json")

except Exception as e:
    print("❌ Error writing file:", e)