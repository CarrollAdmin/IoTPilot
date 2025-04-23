"""
IoTPilot: An AI-powered IoT application development framework.

This module provides the main entry point for the IoTPilot framework, which supports both
single-agent and multi-agent modes for IoT application development and debugging.
"""

from typing import Optional, Dict, Any
import os
import json
import argparse
from pathlib import Path
import logging

from single_agent import single_agent
from multi_agent import multi_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """Parse and return command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="IoTPilot configuration for AI-powered IoT development"
    )
    
    # Execution configuration
    parser.add_argument(
        '--max_attempts',
        type=int,
        default=3,
        help='Maximum number of attempts for self-debugging'
    )
    parser.add_argument(
        '--app_path',
        type=str,
        default='../datasets/app.csv',
        help='Path to user questions dataset'
    )
    
    # Feature flags
    parser.add_argument('--iscontext', type=bool, default=True, help='Enable context awareness')
    parser.add_argument('--isexecution', type=bool, default=False, help='Enable execution')
    parser.add_argument('--isruntime', type=bool, default=False, help='Enable runtime monitoring')
    parser.add_argument('--isruntimedebug', type=bool, default=False, help='Enable runtime debugging')
    parser.add_argument('--ismemory', type=bool, default=True, help='Enable memory persistence')
    
    # System configuration
    parser.add_argument(
        '--device_type',
        type=str,
        default="esp32",
        choices=["esp32", "esp8266", "arduino"],
        help='Target IoT device type'
    )
    parser.add_argument(
        '--os_type',
        type=str,
        default="RIOT",
        choices=["RIOT", "FreeRTOS", "Zephyr"],
        help='Target embedded operating system'
    )
    
    # Agent configuration
    parser.add_argument(
        '--mode',
        type=str,
        default='SingleAgent',
        choices=['SingleAgent', 'MultiAgent'],
        help='Operation mode: SingleAgent or MultiAgent'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o',
        choices=['gpt-4o', 'gpt-4o-mini', 'deepseek-coder'],
        help='AI model to use'
    )
    
    # User inputs
    parser.add_argument('--isuserreq', type=bool, default=False, help='Enable user requirements')
    parser.add_argument(
        '--usereq',
        type=str,
        default='mqtt app typically need to ...',
        help='User requirements for execution logic'
    )
    parser.add_argument('--userproblem', type=str, default="", help='Problem description')
    parser.add_argument('--fix_lines', type=str, default="40", help="Lines to fix")
    parser.add_argument('--username', type=str, default="emm", help="Username for session management")
    
    # API Configuration
    parser.add_argument('--api_key', type=str, default="", help="API key for LLM provider")
    parser.add_argument('--api_base', type=str, default="https://xiaoai.plus/v1", help="API base URL for LLM provider")
    
    # Server configuration
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    
    return parser.parse_args()

def handle_memory_state(username: str, process_id: str, question: str) -> str:
    """Handle memory state persistence and retrieval.
    
    Args:
        username (str): Current username
        process_id (str): Process identifier
        question (str): Original question/problem description
        
    Returns:
        str: Updated question incorporating previous state if available
    """
    file_path = Path(f"output/{username}/{process_id}/-1_state.json")
    
    if file_path.is_file():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                curr_state = json.load(file)
            current_code = curr_state.get('generation', '')
            return f"current code: {current_code} You only need to modify the current code by {question}"
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading memory state: {e}")
            return question
    return question

def iotpilot_func(args: Optional[argparse.Namespace] = None) -> Optional[str]:
    """Main function for IoTPilot framework.
    
    Args:
        args (Optional[argparse.Namespace]): Command line arguments
        
    Returns:
        Optional[str]: Generated code in SingleAgent mode, None in MultiAgent mode
    """
    if args is None:
        args = parse_arguments()
        
    # Set API configuration from arguments
    if not args.api_key:
        logger.error("API key not provided. Please set the api_key parameter or IOTPILOT_API_KEY environment variable.")
        return None
        
    os.environ['IOTPILOT_API_KEY'] = args.api_key
    os.environ['OPENAI_API_KEY'] = args.api_key
    
    if args.api_base:
        os.environ['IOTPILOT_API_BASE'] = args.api_base
        os.environ['OPENAI_API_BASE'] = args.api_base
        
    # Extract arguments
    method_type = "user"
    question = args.userproblem
    
    logger.info(f"Starting generation >>> {question}")
    
    if args.mode == "SingleAgent":
        role = -1
        process_id = "VScode"
        
        if args.ismemory:
            question = handle_memory_state(args.username, process_id, question)
        
        try:
            result = single_agent(
                process_id=process_id,
                model=args.model,
                question=question,
                max_attempts=args.max_attempts,
                iscontext=args.iscontext,
                isexecution=args.isexecution,
                isruntime=args.isruntime,
                isruntimedebug=args.isruntimedebug,
                isuserreq=args.isuserreq,
                usereq=args.usereq,
                program_name=args.username,
                role=role,
                method_type=method_type,
                device_type=args.device_type,
                os_type=args.os_type,
                stream_handler=args.stream_handler if hasattr(args, 'stream_handler') else None
            )
            logger.info("Generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in SingleAgent mode: {e}")
            raise
    
    elif args.mode == "MultiAgent":
        try:
            result = multi_agent(
                process_id=1,  # Default process ID for MultiAgent mode
                model=args.model,
                question=question,
                max_attempts=args.max_attempts,
                iscontext=args.iscontext,
                isexecution=args.isexecution,
                isruntime=args.isruntime,
                isuserreq=args.isuserreq,
                usereq=args.usereq,
                program_name=args.username,
                role=1,
                device_type=args.device_type,
                os_type=args.os_type,
                stream_handler=args.stream_handler if hasattr(args, 'stream_handler') else None
            )
            logger.info("MultiAgent execution completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in MultiAgent mode: {e}")
            raise
    
    else:
        raise ValueError(f"Invalid mode: {args.mode}")

if __name__ == "__main__":
    try:
        result = iotpilot_func()
        if result:
            logger.info("Generation completed successfully")
    except Exception as e:
        logger.error(f"Error during execution: {e}")


