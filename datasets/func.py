import os
import re
import csv

def find_declarations_in_file(file_path, csv_writer, declaration_id):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Patterns for function, struct, class, enum, and include declarations
    function_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\))')
    struct_pattern = re.compile(r'(struct\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{[^}]*\}\s*[a-zA-Z_][a-zA-Z0-9_]*\s*;)')
    class_pattern = re.compile(r'(class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{[^}]*\}\s*;)')
    enum_pattern = re.compile(r'(enum\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{[^}]*\}\s*;)')
    include_pattern = re.compile(r'#include\s*[<"]([^">]+)[">]')

    functions = function_pattern.findall(content)
    structs = struct_pattern.findall(content)
    classes = class_pattern.findall(content)
    enums = enum_pattern.findall(content)
    includes = include_pattern.findall(content)

    for func in functions:
        csv_writer.writerow([declaration_id,  func])
        declaration_id += 1

    for struct in structs:
        csv_writer.writerow([declaration_id,  struct])
        declaration_id += 1

    for cls in classes:
        csv_writer.writerow([declaration_id, cls])
        declaration_id += 1

    for enum in enums:
        csv_writer.writerow([declaration_id, enum])
        declaration_id += 1

    for inc in includes:
        csv_writer.writerow([declaration_id, f'#include {inc}'])
        declaration_id += 1

    return declaration_id

def find_declarations_in_directory(directory, csv_writer, declaration_id):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.c', '.cpp', '.h', '.hpp')):
                file_path = os.path.join(root, file)
                declaration_id = find_declarations_in_file(file_path, csv_writer, declaration_id)
    return declaration_id

def main():
    search_path = 'search.txt'
    paths = []
    with open(search_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            paths.append(line.strip())
    
    csv_file_path = 'output.csv'

    declaration_id = 0
    for path in paths:
        path = str(path)
        print(path)
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            if os.stat(csv_file_path).st_size == 0:
                csv_writer.writerow(["id", "code"])
            if os.path.isdir(path):
                declaration_id = find_declarations_in_directory(path, csv_writer, declaration_id)
            elif os.path.isfile(path):
                declaration_id = find_declarations_in_file(path, csv_writer, declaration_id)
            else:
                print(f"path:{path} is invalid")

if __name__ == "__main__":
    main()
