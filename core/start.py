#!/usr/bin/env python3
"""
IoTPilot - A framework for Embedded IoT application development.

This module serves as the entry point for the IoTPilot framework, handling configuration
and orchestration of single or multi-agent code generation processes.
"""

import argparse
import logging
import threading
import os
from typing import Dict, List, Optional
from pathlib import Path

from single_agent import single_agent
from multi_agent import multi_agent
from libs import data_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


SUPPORTED_OS = {
    "Contiki": [
        "Contiki_DHT11",
        "Contiki_led",
        "Contiki_UDP",
        "Contiki_COAP",
        "Contiki_MQTT",
    ],
    "Zephyr": [
        "Zephyr_MQTT",
        "Zephyr_COAP",
        "Zephyr_IRQ",
        "Zephyr_UDP",
        "Zephyr_MMA",
    ],
    "FreeRTOS": [
        "FreeRTOS_MQTT",
        "FreeRTOS_COAP",
        "FreeRTOS_UDP",
        "FreeRTOS_FLASH",
        "FreeRTOS_MMA",
    ],
    "RIOT": [
        "RIOT_MQTT",
        "RIOT_COAP",
        "RIOT_MQTT_SN",
        "RIOT_IRQ",
        "RIOT_RTC",
        "RIOT_UDP",
        "RIOT_Thread",
        "RIOT_Timer",
        "RIOT_Flash",
        "RIOT_MMA",
        "RIOT_Event",
        "RIOT_DHT11",
        "RIOT_Warn",
        "RIOT_Sched",
        "RIOT_MBOX"
    ]
}

def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="IoTPilot - A framework for IoT application development and testing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Configuration arguments
    parser.add_argument('--max_attempts', type=int, default=10,
                      help='Maximum number of attempts for self-debug')
    parser.add_argument('--app_path', type=str, default='../datasets/app.csv',
                      help='Path to user questions dataset')
    parser.add_argument('--device_type', type=str, default="esp32",
                      choices=["esp32"], help='Target device type')
    parser.add_argument('--os_type', type=str, default="RIOT",
                      choices=list(SUPPORTED_OS.keys()), help='Target embedded OS')
    
    # Feature flags
    parser.add_argument('--iscontext', type=bool, default=True,
                      help='Enable context-aware code generation')
    parser.add_argument('--isexecution', type=bool, default=False,
                      help='Enable execution-aware code generation')
    parser.add_argument('--isruntime', type=bool, default=False,
                      help='Enable runtime monitoring')
    parser.add_argument('--isruntimedebug', type=bool, default=False,
                      help='Enable runtime debugging')
    
    # Agent configuration
    parser.add_argument('--mode', type=str, default='SingleAgent',
                      choices=['SingleAgent', 'MultiAgent'],
                      help='Agent operation mode')
    parser.add_argument('--model', type=str, default='deepseek-coder',
                      choices=['gpt-4o', 'deepseek-coder'],
                      help='Model to use for code generation')
    
    # API Configuration
    parser.add_argument('--api_key', type=str, default="",
                      help="API key for LLM provider")
    parser.add_argument('--api_base', type=str, default="",
                      help="API base URL for LLM provider")
    
    # User requirements
    parser.add_argument('--isuserreq', type=bool, default=False,
                      help='Enable user requirements processing')
    parser.add_argument('--usereq', type=str,
                      default='mqtt app typically need to ...',
                      help='User requirements specification')
    
    args = parser.parse_args()
    return args

def run_single_agent(args: argparse.Namespace, code_name: str, data_dict: Dict[str, str]) -> None:
    """Run the single agent code generation process.

    Args:
        args: Command line arguments
        code_name: Name of the code to generate
        data_dict: Dictionary containing code generation tasks
    """
    threads = []
    role = -1
    method_type = "deepseeker-coder"
    process_ids = 6
    
    for process_id in range(1, process_ids):
        thread = threading.Thread(
            target=single_agent,
            args=(
                process_id, args.model, data_dict[code_name],
                args.max_attempts, args.iscontext, args.isexecution,
                args.isruntime, args.isruntimedebug, args.isuserreq,
                args.usereq, code_name, role, method_type,
                args.device_type, args.os_type
            )
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

def run_multi_agent(args: argparse.Namespace, code_name: str, data_dict: Dict[str, str]) -> None:
    """Run the multi-agent code generation process.

    Args:
        args: Command line arguments
        code_name: Name of the code to generate
        data_dict: Dictionary containing code generation tasks
    """
    threads = []
    role = -1
    process_ids = 1
    method_type = "deepseeker-coder"
    
    for process_id in range(0, process_ids):
        thread = threading.Thread(
            target=multi_agent,
            args=(
                process_id, args.model, data_dict[code_name],
                args.max_attempts, args.iscontext, args.isexecution,
                args.isruntime, args.isuserreq, args.usereq,
                code_name, role, method_type,
                args.device_type, args.os_type
            )
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

def main(args: Optional[argparse.Namespace] = None) -> None:
    """Main entry point for the IoTPilot framework.

    Args:
        args: Optional command line arguments. If None, arguments will be parsed from sys.argv
    """
    if args is None:
        args = parse_arguments()
    
    # Set API configuration from arguments
    if not args.api_key or not args.api_base:
        logger.error("API key not provided. Please set the api_key parameter or api_base environment variable.")
        return
    
    if args.api_base:
        os.environ['OPENAI_API_KEY'] = args.api_key
        os.environ['OPENAI_API_BASE'] = args.api_base
    
    try:
        # Load application data
        data_dict = data_loader(args.app_path)
        if not data_dict:
            logger.error("Failed to load application data")
            return
        
        # Get supported applications for the selected OS
        code_names = SUPPORTED_OS.get(args.os_type)
        if not code_names:
            logger.error(f"Invalid OS type: {args.os_type}")
            return
            
        # Process each application
        for code_name in code_names:
            logger.info(f"Processing {code_name}")
            logger.debug(f"Task description: {data_dict[code_name]}")
            
            if args.mode == "SingleAgent":
                run_single_agent(args, code_name, data_dict)
            elif args.mode == "MultiAgent":
                run_multi_agent(args, code_name, data_dict)
            else:
                logger.error(f"Invalid mode: {args.mode}")
                return
                
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()


