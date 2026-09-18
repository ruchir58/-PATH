import os
import glob

search_dir = r"c:\Users\The LOQ\Desktop\प्रगतिPATH\frontend\src"

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace "http://localhost:8005/..." with `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/...`
    new_content = content.replace('"http://localhost:8005/', '`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8005\'}/')
    # Fix the trailing quote that was left over from the original double quotes
    new_content = new_content.replace('/datasets/upload", formData', '/datasets/upload`, formData')
    
    # Replace `http://localhost:8005/...`
    new_content = new_content.replace('`http://localhost:8005/', '`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8005\'}/')

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        pass

for root, _, files in os.walk(search_dir):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            replace_in_file(os.path.join(root, file))
