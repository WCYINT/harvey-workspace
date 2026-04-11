import re

# Read chapter 5 content
with open('/Users/fhjtech/.openclaw/workspace/.tmp_paper/chapter5_analysis.txt', 'r') as f:
    text = f.read()

# Check for data consistency issues
print("=== LOGICAL ISSUE ANALYSIS ===\n")

# Issue 1: Inconsistent numbers
print("1. DATA CONSISTENCY ISSUES:")
print("-" * 50)

# VRS1 numbers
vrs1_72 = re.search(r'VRS1.*?均值.*?72', text)
vrs1_739 = re.search(r'VRS1.*?73\.9', text)
print(f"   VRS1均值72个: {'FOUND' if vrs1_72 else 'NOT FOUND'}")
print(f"   VRS1均值73.9: {'FOUND' if vrs1_739 else 'NOT FOUND'}")

# VRS2.1 numbers  
vrs21_46 = re.search(r'VRS2\.1.*?46', text)
print(f"   VRS2.1均值46个: {'FOUND' if vrs21_46 else 'NOT FOUND'}")

# EL2 numbers
el2 = re.search(r'EL2.*?6\.7', text)
print(f"   EL2均值6.7: {'FOUND' if el2 else 'NOT FOUND'}")

# Issue 2: Table reference issues
print("\n2. TABLE/FIGURE REFERENCE ISSUES:")
print("-" * 50)
table_refs = re.findall(r'(?:表|图)[4-5]-\d+', text)
unique_refs = set(table_refs)
print(f"   References found: {sorted(unique_refs)}")

# Issue 3: Cross-chapter references that seem wrong for Chapter 5
print("\n3. CROSS-REFERENCES IN CHAPTER 5:")
print("-" * 50)
ch4_refs = re.findall(r'(?:表|图)4-\d+', text)
print(f"   References to Chapter 4 tables/figures: {ch4_refs}")

# Issue 4: Statistical test results
print("\n4. STATISTICAL ANALYSIS ISSUES:")
print("-" * 50)
# Check T-test results
ttest = re.search(r'T\s*值.*?自由度.*?P\s*值.*?10\.3117.*?0\.000', text, re.DOTALL)
print(f"   T-test table (T=10.3117, P=0.000): {'COMPLETE' if ttest else 'INCOMPLETE OR NOT FOUND'}")

# Issue 5: 表5-7 data format
print("\n5. TABLE 5-7 DATA FORMAT:")
print("-" * 50)
# Find the table data
table5_7 = re.search(r'表5-7.*?(?:VRS1|VRS2\.1|VRS2\.2|EL1|EL2).*?\d+', text, re.DOTALL)
if table5_7:
    print("   Table 5-7 data section found")
    # Check alignment
    rows = re.findall(r'\d+', table5_7.group())
    print(f"   Numbers in table: {rows[:20]}...")

# Issue 6: 摘要 vs 正文 consistency
print("\n6. ABSTRACT vs CHAPTER 5 CONSISTENCY:")
print("-" * 50)
# IQF improvement
iqf_39 = re.search(r'39%', text)
iqf_36 = re.search(r'36%', text)
print(f"   降幅39%: {'FOUND' if iqf_39 else 'NOT FOUND'}")
print(f"   降幅36%: {'FOUND' if iqf_36 else 'NOT FOUND'}")
print("   NOTE: 摘要 says 39%, section 5.3 says 36% - INCONSISTENT!")

print("\n=== SUMMARY ===")
print("Main logical issues identified:")
print("1. VRS1均值 inconsistency (72 vs 73.9)")
print("2. 降幅 inconsistency (摘要39% vs 5.3节36%)")
print("3. Cross-references to Chapter 4 figures in Chapter 5 content")
print("4. EL2 vs VRS2.1 data mismatch in improvement description")
