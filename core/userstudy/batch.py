import csv
import os
import subprocess
import json

def create_curl_command(username, userproblem):
    return f"""curl -X POST http://47.102.103.1:20018/run \\
-H "Content-Type: application/json" \\
-d '{{
  "username": "{username}",
  "userproblem": "{userproblem}",
  "max_attempts": 10,
  "iscontext": "True",
  "model": "gpt-4o",
  "os_type": "RIOT",
  "device_type": "esp32"
}}'"""

def execute_curl_command(curl_command):
    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        return response.get('code', '')
    except subprocess.CalledProcessError as e:
        print(f"Error executing curl command: {e}")
        return ''
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return ''

def main():
    csv_file_path = '../datasets/userstudy.csv'
    
    root_dir = os.path.join(os.getcwd(), 'userstudy')
    os.makedirs(root_dir, exist_ok=True)
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            username = row['username']
            userproblem = row['prompt']
            
            curl_command = create_curl_command(username, userproblem)
            
            code = execute_curl_command(curl_command)
            
            user_dir = os.path.join(root_dir, username)
            os.makedirs(user_dir, exist_ok=True)
            
            if code:
                code_file_path = os.path.join(user_dir, 'generated_code.c')
                with open(code_file_path, 'w') as code_file:
                    code_file.write(code)
                print(f"Code for {username} written to {code_file_path}")
            else:
                print(f"Failed to retrieve code for {username}")

if __name__ == "__main__":
    main()