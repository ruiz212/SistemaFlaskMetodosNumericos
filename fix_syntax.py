with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if i == 270:  # line 271 (0-indexed = 270)
        # Replace the bad line with the correct one
        lines[i] = "            return jsonify({'error': f'Error en expresi\u00f3n: {str(e)}'})\n"
        print(f"Fixed line {i+1}: {lines[i].strip()}")

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done writing.")
