import json
import re
import sys
import os

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def get_filename(path):
    return os.path.basename(path)

def reorder_pages(pages):
    if isinstance(pages, list):
        # Find the "overview" item
        overview_item = next((item for item in pages if isinstance(item, str) and item.lower().endswith("/overview")), None)
        
        # Remove the "overview" item from the list
        if overview_item:
            pages = [item for item in pages if item != overview_item]

        # Separate items into groups, regular pages, and special pages
        regular_groups = []
        special_groups = {'_': [], '.': []}
        regular_pages = []
        special_pages = {'_': [], '.': []}

        for item in pages:
            if isinstance(item, dict) and 'group' in item:
                if item['group'].startswith('_'):
                    special_groups['_'].append(item)
                elif item['group'].startswith('.'):
                    special_groups['.'].append(item)
                else:
                    regular_groups.append(item)
            elif isinstance(item, str):
                filename = get_filename(item)
                if filename.startswith('_'):
                    special_pages['_'].append(item)
                elif filename.startswith('.'):
                    special_pages['.'].append(item)
                else:
                    regular_pages.append(item)
            else:
                regular_pages.append(item)

        # Sort regular groups
        sorted_regular_groups = sorted(regular_groups, key=lambda x: natural_sort_key(x['group']))

        # Sort special groups
        sorted_special_groups = sorted(special_groups['_'], key=lambda x: natural_sort_key(x['group'])) + sorted(special_groups['.'], key=lambda x: natural_sort_key(x['group']))

        # Combine all sorted groups
        sorted_groups = sorted_regular_groups + sorted_special_groups

        # Sort regular pages
        sorted_regular_pages = sorted(regular_pages, key=lambda x: natural_sort_key(x if isinstance(x, str) else x.get('group', '')))

        # Sort special pages
        sorted_special_pages = sorted(special_pages['_'], key=natural_sort_key) + sorted(special_pages['.'], key=natural_sort_key)

        # Combine all sorted items
        sorted_pages = sorted_groups + sorted_regular_pages + sorted_special_pages

        # Add the "overview" item back to the beginning if it exists
        if overview_item:
            sorted_pages.insert(0, overview_item)

        # Recursively reorder nested "pages"
        for item in sorted_pages:
            if isinstance(item, dict) and 'pages' in item:
                item['pages'] = reorder_pages(item['pages'])

        return sorted_pages
    return pages

def process_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'pages':
                data[key] = reorder_pages(value)
            elif isinstance(value, (dict, list)):
                process_json(value)
    elif isinstance(data, list):
        for item in data:
            process_json(item)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Generate output filename
    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_reordered{file_extension}"

    # Load the JSON data
    with open(input_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{input_file}': {e}")
            sys.exit(1)

    # Process the JSON data
    process_json(data)

    # Write the modified JSON data back to a file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"JSON file has been processed and saved as '{output_file}'.")

if __name__ == "__main__":
    main()
