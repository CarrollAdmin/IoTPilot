"""
IoTPilot Gateway Server

This module implements a Flask-based gateway server for the IoTPilot framework.
It provides both REST API and WebSocket endpoints for code generation and execution,
supporting real-time communication with clients.

The server handles:
- Code generation requests
- Real-time execution monitoring
- WebSocket-based progress updates
- User session management
"""

from flask import Flask, request, jsonify
import subprocess
import threading
from flask_cors import CORS
import argparse
import json
from flask_socketio import SocketIO, emit
from typing import Optional, Dict, Any, Union
import logging
from io import StringIO
from iotpilot import *
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogCapture:
    """Capture logs in a string buffer."""
    
    def __init__(self):
        """Initialize the log capture handler."""
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.root_logger = logging.getLogger() 
        
    def __enter__(self):
        """Start capturing logs."""
        # Add handler to all loggers
        self.root_logger.addHandler(self.handler)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing logs."""
        # Remove handler from all loggers
        self.root_logger.removeHandler(self.handler)
        self.handler.close()
        
    def get_logs(self) -> str:
        """Get captured logs.
        
        Returns:
            str: Captured log messages
        """
        return self.log_stream.getvalue()

def create_arg_parser() -> argparse.ArgumentParser:
    """Create and configure command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description="IoTPilot Gateway Configuration")
    
    # Execution parameters
    parser.add_argument(
        '--max_attempts',
        type=int,
        default=1,
        help='Maximum number of attempts for self-debugging'
    )
    parser.add_argument(
        '--app_path',
        type=str,
        default='../datasets/app.csv',
        help='Path to user questions dataset'
    )
    
    # Feature flags
    parser.add_argument(
        '--iscontext',
        type=bool,
        default=False,
        help='Enable context-aware code generation'
    )
    parser.add_argument(
        '--isexecution',
        type=bool,
        default=False,
        help='Enable execution monitoring'
    )
    parser.add_argument(
        '--isruntime',
        type=bool,
        default=False,
        help='Enable runtime monitoring'
    )
    parser.add_argument(
        '--isruntimedebug',
        type=bool,
        default=False,
        help='Enable runtime debugging'
    )
    
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
        choices=["RIOT", "FreeRTOS", "Zephyr", "Contiki"],
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
    
    # User requirements
    parser.add_argument(
        '--isuserreq',
        type=bool,
        default=False,
        help='Enable user requirements processing'
    )
    parser.add_argument(
        '--usereq',
        type=str,
        default='mqtt app typically need to ...',
        help='User requirements for execution logic'
    )
    parser.add_argument(
        '--userproblem',
        type=str,
        default="",
        help='Problem description'
    )
    parser.add_argument(
        '--fix_lines',
        type=str,
        default="44",
        help="Lines to fix in the code"
    )
    parser.add_argument(
        '--ismemory',
        type=bool,
        default=True,
        help="Enable memory persistence"
    )
    parser.add_argument(
        '--username',
        type=str,
        default="",
        help="Username for session management"
    )
    
    # API Configuration
    parser.add_argument(
        '--api_key',
        type=str,
        default="sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo",
        help="API key for LLM provider"
    )
    parser.add_argument(
        '--api_base',
        type=str,
        default="https://xiaoai.plus/v1",
        help="API base URL for LLM provider"
    )
    
    return parser

# Initialize Flask application
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class StreamHandler:
    """Handler for streaming updates to WebSocket clients."""
    
    def __init__(self, sid: str):
        """Initialize stream handler.
        
        Args:
            sid: Socket ID of the client
        """
        self.sid = sid

    def add_to_stream(self, data: Dict[str, Any]) -> None:
        """Send update to the client.
        
        Args:
            data: Update data to send
        """
        socketio.emit('stream_update', data, room=self.sid)

def run_iotpilot(
    userproblem: str,
    username: Optional[str] = None,
    sid: Optional[str] = None,
    max_attempts: Optional[int] = None,
    iscontext: Optional[bool] = None,
    model: Optional[str] = None,
    os_type: Optional[str] = None,
    device_type: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None
) -> Union[str, Dict[str, Any]]:
    """Run IoTPilot code generation and execution.
    
    Args:
        userproblem: Problem description or requirements
        username: Optional username for session management
        sid: Optional socket ID for real-time updates
        max_attempts: Optional maximum number of attempts for self-debugging
        iscontext: Optional flag to enable/disable context-aware generation
        model: Optional AI model to use
        os_type: Optional target embedded operating system
        device_type: Optional target IoT device type
        api_key: Optional API key for LLM provider
        api_base: Optional API base URL for LLM provider
        
    Returns:
        Generated code or error message
        
    Raises:
        Exception: If code generation fails
    """
    with LogCapture() as log_capture:
        try:
            if username:
                args.username = username
            if max_attempts is not None:
                args.max_attempts = max_attempts
            if iscontext is not None:
                args.iscontext = iscontext
            if model:
                args.model = model
            if os_type:
                args.os_type = os_type
            if device_type:
                args.device_type = device_type
            if api_key:
                args.api_key = api_key
                os.environ['OPENAI_API_KEY'] = api_key
            else:
                return {
                    'error': 'API key is required',
                    'logs': 'API key not provided. Please set the api_key parameter.'
                }
            if api_base:
                args.api_base = api_base
                os.environ['OPENAI_API_BASE'] = api_base
            args.userproblem = userproblem
            if sid:
                args.stream_handler = StreamHandler(sid)
            results = iotpilot_func(args)
            
            # Return both results and logs
            return {
                'code': results,
                'logs': log_capture.get_logs()
            }
        except Exception as e:
            logger.error(f"Error in run_iotpilot: {str(e)}")
            return {
                'error': str(e),
                'logs': log_capture.get_logs()
            }

@app.route('/run', methods=['POST'])
def run() -> tuple[Any, int]:
    """Handle POST requests for code generation.
    
    Returns:
        Tuple of (response, status_code)
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        userproblem = data.get('userproblem')
        max_attempts = data.get('max_attempts')
        iscontext = data.get('iscontext')
        model = data.get('model')
        os_type = data.get('os_type')
        device_type = data.get('device_type')
        api_key = data.get('api_key')
        api_base = data.get('api_base')

        if not userproblem:
            return jsonify({'error': 'Userproblem is required'}), 400
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        if iscontext == "False":
            iscontext = False
        elif iscontext == "True":
            iscontext = True    
        else:
            return jsonify({'error': 'iscontext is invalid'}), 400
        if model not in ['gpt-4o', 'gpt-4o-mini', 'deepseek-coder']:
            return jsonify({'error': 'Invalid model specified'}), 400
        if os_type not in ['RIOT', 'FreeRTOS', 'Zephyr', 'Contiki']:
            return jsonify({'error': 'Invalid os_type specified'}), 400
        if device_type not in ['esp32', 'esp8266', 'arduino']:
            return jsonify({'error': 'Invalid device_type specified'}), 400
        
        logger.info(f"Processing request for user: {username}")
        logger.info(f"Configuration - max_attempts: {max_attempts}, iscontext: {iscontext}, model: {model}, os_type: {os_type}, device_type: {device_type}")
        result = run_iotpilot(
            userproblem,
            username,
            0,
            max_attempts,
            iscontext,
            model,
            os_type=os_type,
            device_type=device_type,
            api_key=api_key,
            api_base=api_base
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': str(e),
            'logs': 'Error occurred before log capture could start'
        }), 500

@socketio.on("connect", namespace="/ws")
def handle_connect() -> None:
    """Handle WebSocket client connection."""
    logger.info(f'Client connected: {request.sid}')

@socketio.on("disconnect", namespace="/ws")
def handle_disconnect() -> None:
    """Handle WebSocket client disconnection."""
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('run_task', namespace="/ws")
def handle_run_task(data: Dict[str, Any]) -> None:
    """Handle WebSocket task execution requests.
    
    Args:
        data: Task execution parameters
    """
    try:
        username = data.get('username')
        userproblem = data.get('userproblem')
        max_attempts = data.get('max_attempts')
        iscontext = data.get('iscontext')
        model = data.get('model')
        os_type = data.get('os_type')
        device_type = data.get('device_type')
        api_key = data.get('api_key')
        api_base = data.get('api_base')

        if not userproblem:
            emit('error', {'message': 'Userproblem is required'})
            return
            
        if not api_key:
            emit('error', {'message': 'API key is required'})
            return

        if max_attempts is not None:
            try:
                max_attempts = int(max_attempts)
                if max_attempts <= 0:
                    emit('error', {'message': 'max_attempts must be positive'})
                    return
            except ValueError:
                emit('error', {'message': 'max_attempts must be an integer'})
                return

        if iscontext is not None and not isinstance(iscontext, bool):
            emit('error', {'message': 'iscontext must be a boolean'})
            return

        if model not in ['gpt-4o', 'gpt-4o-mini', 'deepseek-coder']:
            emit('error', {'message': 'Invalid model specified'})
            return

        if os_type not in ['RIOT', 'FreeRTOS', 'Zephyr', 'Contiki']:
            emit('error', {'message': 'Invalid os_type specified'})
            return

        if device_type not in ['esp32', 'esp8266', 'arduino']:
            emit('error', {'message': 'Invalid device_type specified'})
            return

        logger.info(f"Running task for user: {username or 'anonymous'}")
        logger.info(f"Configuration - max_attempts: {max_attempts}, iscontext: {iscontext}, model: {model}, os_type: {os_type}, device_type: {device_type}")
        
        def run_task() -> None:
            try:
                result = run_iotpilot(
                    userproblem,
                    username,
                    request.sid,
                    max_attempts=max_attempts,
                    iscontext=iscontext,
                    model=model,
                    os_type=os_type,
                    device_type=device_type,
                    api_key=api_key,
                    api_base=api_base
                )
                # Send both code and logs
                if isinstance(result, dict):
                    emit('task_complete', result)
                else:
                    emit('task_complete', {'error': 'Unexpected result format'})
            except Exception as e:
                logger.error(f"Task execution error: {str(e)}")
                emit('error', {
                    'message': str(e),
                    'logs': 'Error occurred during execution'
                })

        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"Error handling task: {str(e)}")
        emit('error', {
            'message': str(e),
            'logs': 'Error occurred before task execution'
        })

if __name__ == '__main__':
    
    args = create_arg_parser().parse_args()
    
    # Start the server
    logger.info("Starting IoTPilot Gateway Server...")
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
