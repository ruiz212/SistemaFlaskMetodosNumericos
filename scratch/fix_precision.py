import os
import re

dir_path = "metodos"

for file_name in os.listdir(dir_path):
    if not file_name.endswith(".py"): continue
    
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We want to replace: f"{var:.6f}" with var
    # But carefully! For example:
    # 'a': f"{a:.6f}"  -> 'a': a
    
    # Regex to find: f"{var:.6f}"
    # capturing the var part.
    new_content = re.sub(r'f"\{([a-zA-Z0-9_]+):\.6f\}"', r'\1', content)
    
    # Also replace things like f"{error_rp.real:.6f}%" -> we leave these alone or handle them in JS.
    # Actually, we can replace :.6f with nothing for errors if we want raw string, but it's fine as is.
    # Or replace :.6f with :.10f
    
    # Just to be safe, let's just replace all :.6f with :.15f so Python sends high precision strings.
    # That is MUCH safer and doesn't break JS that expects strings!
    new_content_safe = content.replace(":.6f}", ":.15f}")
    new_content_safe = new_content_safe.replace(":.4f}", ":.15f}")
    
    if content != new_content_safe:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content_safe)
        print(f"Updated {file_name}")
