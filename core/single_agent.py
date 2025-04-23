#!/usr/bin/env python3
"""
Single Agent Module for IoTPilot Framework.

This module implements the single-agent approach for IoT code generation and testing.
It handles the compilation, execution, and runtime debugging of generated code using
a single agent that iteratively improves the solution based on feedback.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import json
from libs import (
    CodeState, code_gen, compiler, injected_code_gen,
    executor, refine_code, chat_chain, code_task_chain
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration class for single agent parameters."""
    process_id: str
    model: str
    question: str
    max_attempts: int
    iscontext: bool
    isexecution: bool
    isruntime: bool
    isruntimedebug: bool
    isuserreq: bool
    usereq: str
    program_name: str
    role: int
    method_type: str
    device_type: str
    os_type: str
    stream_handler: Optional[Any] = None

def compile_code(
    config: AgentConfig,
    compile_state: CodeState,
    whitelist: List[str],
    blacklist: List[str],
    correct_lists: List[str]
) -> Tuple[bool, str]:
    """Compile the generated code and handle compilation errors.

    Args:
        config: Agent configuration parameters
        compile_state: Current state of code compilation
        whitelist: List of approved APIs/headers
        blacklist: List of forbidden APIs/headers
        correct_lists: List of verified correct APIs/headers

    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    # try:
    #     # Stream compilation status if handler available
    #     if config.stream_handler:
    #         config.stream_handler.add_to_stream({
    #             'type': 'status',
    #             'message': 'Starting code generation and compilation'
    #         })
            
    code_gen(
        config.process_id, config.model, compile_state, None,
        config.question, config.iscontext, config.isexecution,
        config.isuserreq, config.usereq, whitelist, blacklist,
        correct_lists, config.program_name, config.role,
        config.method_type, config.device_type, config.os_type
    )
        
    compiler(compile_state, config.device_type, config.os_type)
    compile_state.to_json(
        compile_state.iterations, -1,
        config.program_name, config.process_id,
        config.method_type
    )
        
        # Stream compilation result
        # if config.stream_handler:
        #     config.stream_handler.add_to_stream({
        #         'type': 'compilation',
        #         'success': compile_state.errorstate == "pass",
        #         'error': compile_state.error if compile_state.errorstate != "pass" else None
        #     })
            
    return compile_state.errorstate == "pass", compile_state.error
        
    # except Exception as e:
    #     logger.error(f"Compilation error: {str(e)}")
    #     if config.stream_handler:
    #         config.stream_handler.add_to_stream({
    #             'type': 'error',
    #             'message': f"Compilation error: {str(e)}"
    #         })
    #     return False, str(e)

def execute_runtime_tests(
    config: AgentConfig,
    compile_state: CodeState
) -> Optional[str]:
    """Execute runtime tests and debugging if enabled.

    Args:
        config: Agent configuration parameters
        compile_state: Successfully compiled code state

    Returns:
        Optional[str]: Generated code after runtime testing and debugging
    """
    try:
        executor_state = CodeState()
        executor_state.generation = compile_state.generation
        attempts = 0

        while executor_state.errorstate != "pass" and attempts <= config.max_attempts:
            attempts += 1
            
            if config.stream_handler:
                config.stream_handler.add_to_stream({
                    'type': 'status',
                    'message': f"Runtime test attempt {attempts}/{config.max_attempts}"
                })
            
            if config.isruntimedebug:
                logger.info("Injecting debug code...")
                injected_code_gen(config.model, executor_state, config.question)
            
            compiler(executor_state, config.device_type, config.os_type)
            
            if executor_state.errorstate == "pass":
                logger.info("Running executor...")
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'status',
                        'message': "Executing runtime tests"
                    })
                    
                executor(executor_state, 10)
                
                if config.isruntimedebug:
                    logger.info("Refining code based on runtime feedback...")
                    refine_code(config.model, executor_state, config.question)
                
                executor_state.to_json(
                    executor_state.iterations, -1,
                    config.program_name, config.process_id,
                    config.method_type
                )
                
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'runtime',
                        'success': True,
                        'logs': executor_state.runtimelogs
                    })
                    
                return executor_state.generation
                
        logger.warning("Runtime tests failed to pass within max attempts")
        if config.stream_handler:
            config.stream_handler.add_to_stream({
                'type': 'runtime',
                'success': False,
                'message': "Runtime tests failed to pass within max attempts"
            })
        return None
        
    except Exception as e:
        logger.error(f"Runtime execution error: {str(e)}")
        if config.stream_handler:
            config.stream_handler.add_to_stream({
                'type': 'error',
                'message': f"Runtime execution error: {str(e)}"
            })
        return None

def single_agent(
    process_id: str,
    model: str,
    question: str,
    max_attempts: int,
    iscontext: bool,
    isexecution: bool,
    isruntime: bool,
    isruntimedebug: bool,
    isuserreq: bool,
    usereq: str,
    program_name: str,
    role: int,
    method_type: str,
    device_type: str,
    os_type: str,
    stream_handler: Optional[Any] = None
) -> Optional[str]:
    """Main entry point for single agent code generation and testing.

    This function implements the single-agent approach for generating and testing IoT code.
    It handles both compilation and runtime phases, with optional debugging capabilities.

    Args:
        process_id: Unique identifier for the process
        model: Name of the model to use for code generation
        question: The programming task description
        max_attempts: Maximum number of attempts for compilation/runtime
        iscontext: Whether to use context-aware generation
        isexecution: Whether to use execution-aware generation
        isruntime: Whether to perform runtime testing
        isruntimedebug: Whether to enable runtime debugging
        isuserreq: Whether to consider user requirements
        usereq: User requirements specification
        program_name: Name of the program being generated
        role: Role identifier for the agent
        method_type: Type of method being used
        device_type: Target device type
        os_type: Target operating system type
        stream_handler: Optional handler for streaming updates

    Returns:
        Optional[str]: The generated code if successful, None otherwise
    """
    try:
        config = AgentConfig(
            process_id=process_id,
            model=model,
            question=question,
            max_attempts=max_attempts,
            iscontext=iscontext,
            isexecution=isexecution,
            isruntime=isruntime,
            isruntimedebug=isruntimedebug,
            isuserreq=isuserreq,
            usereq=usereq,
            program_name=program_name,
            role=role,
            method_type=method_type,
            device_type=device_type,
            os_type=os_type,
            stream_handler=stream_handler
        )
        
        # Determine whether RAG is needed
        print(f"process_id: {process_id} start")
        codetask_chain_oai = code_task_chain(model)
        codetask_solution = codetask_chain_oai.invoke(
            {"question": str(question)}
        )
    
        
        if codetask_solution.type == "Yes":
            logger.info("Detected coding task")
        else:
            logger.info("Detected non-coding task")
            
            chat_chain_oai = chat_chain(model)
            chat_solution = chat_chain_oai.invoke(
                {"question": str(question)}
            )
            return chat_solution.answer

        compile_state = CodeState()
        attempts = 1
        whitelist = []
        blacklist = []
        correct_lists = []
        print(f"process_id: {process_id})")
        # Compilation phase
        while attempts <= int(max_attempts):
            logger.info(f"Compilation attempt, {process_id}: {attempts}/{max_attempts}")
            attempts += 1
            
            success, error = compile_code(
                config, compile_state, whitelist,
                blacklist, correct_lists
            )
            
            if success:
                logger.info("Compilation successful")
                break

        # Runtime phase
        if config.isruntime and compile_state.errorstate == "pass":
            logger.info("Starting runtime tests...")
            final_code = execute_runtime_tests(config, compile_state)
            if final_code:
                if stream_handler:
                    stream_handler.add_to_stream({
                        'type': 'result',
                        'data': final_code
                    })
                return final_code
            logger.warning("Runtime tests failed")

        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'result',
                'data': compile_state.generation
            })
        return compile_state.generation

    except Exception as e:
        logger.error(f"Single agent execution failed: {str(e)}")
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'error',
                'message': f"Single agent execution failed: {str(e)}"
            })
        return None
        