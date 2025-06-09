#!/usr/bin/env python3
import re
import sys

def fix_mermaid_html(html_content):
    """
    Convert mermaid code blocks from <pre class="mermaid"><code>...</code></pre>
    to <div class="mermaid">...</div> format that Mermaid.js expects
    """
    
    # Pattern to match mermaid code blocks
    pattern = r'<pre class="mermaid"><code>(.*?)</code></pre>'
    
    def replace_mermaid(match):
        # Extract the mermaid code and clean it up
        mermaid_code = match.group(1)
        
        # Decode HTML entities
        mermaid_code = mermaid_code.replace('&gt;', '>')
        mermaid_code = mermaid_code.replace('&lt;', '<')
        mermaid_code = mermaid_code.replace('&amp;', '&')
        mermaid_code = mermaid_code.replace('&quot;', '"')
        
        # Return as div element
        return f'<div class="mermaid">\n{mermaid_code}\n</div>'
    
    # Apply the replacement
    fixed_html = re.sub(pattern, replace_mermaid, html_content, flags=re.DOTALL)
    
    return fixed_html

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 fix_mermaid.py input.html output.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Read the input HTML file
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Fix the mermaid blocks
        fixed_html = fix_mermaid_html(html_content)
        
        # Write the fixed HTML to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_html)
        
        print(f"Fixed mermaid diagrams in {input_file} and saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 