#!/usr/bin/env python3
"""
Multi-Agent Module for IoTPilot Framework.

This module implements the multi-agent approach for IoT code generation and testing.
It uses a three-phase process:
1. Outline Agent: Breaks down the problem into smaller modules
2. Code Agents: Generate code for each module independently
3. Integration Agent: Combines the module solutions into a complete application
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from libs import (
    CodeState, outline, code_gen, compiler,
    intergration_gen
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MultiAgentConfig:
    """Configuration class for multi-agent parameters."""
    process_id: int
    model: str
    question: str
    max_attempts: int
    iscontext: bool
    isexecution: bool
    isruntime: bool
    isuserreq: bool
    usereq: str
    program_name: str
    role: int
    device_type: str = "Esp32"
    os_type: str = "RIOT"
    method_type: str = "gpt4o"
    stream_handler: Optional[Any] = None

def outline_agent(model: str, question: str, process_id: int, stream_handler: Optional[Any] = None) -> List[str]:
    """Generate an outline of modules needed to solve the problem.
    
    Args:
        model: The model to use for generating the outline
        question: The programming task description
        process_id: Unique identifier for the process
        stream_handler: Optional handler for streaming updates
        
    Returns:
        List[str]: List of module descriptions/subtasks
    """
    try:
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'status',
                'message': f"Generating outline for task: {question[:50]}..."
            })
            
        logger.info(f"Generating outline for task: {question[:50]}...")
        modules = outline(model, question)
        
        if not modules:
            logger.warning("Outline generation returned empty modules list")
            if stream_handler:
                stream_handler.add_to_stream({
                    'type': 'error',
                    'message': "Outline generation failed - no modules generated"
                })
            return []
            
        logger.info(f"Generated {len(modules)} modules")
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'outline',
                'modules': modules
            })
            
        for i, module in enumerate(modules, 1):
            logger.debug(f"Module {i}: {module[:50]}...")
            
        return modules
        
    except Exception as e:
        logger.error(f"Outline agent failed: {str(e)}")
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'error',
                'message': f"Outline agent failed: {str(e)}"
            })
        return []

def code_agents(config: MultiAgentConfig, modules: List[str]) -> List[str]:
    """Generate code for each module independently.
    
    Args:
        config: Configuration parameters for the agents
        modules: List of module descriptions to implement
        
    Returns:
        List[str]: List of generated code solutions for each module
    """
    sub_solutions = []
    
    for count, module_question in enumerate(modules, start=1):
        if config.stream_handler:
            config.stream_handler.add_to_stream({
                'type': 'status',
                'message': f"Generating code for module {count}/{len(modules)}"
            })
            
        logger.info(f"Generating code for module {count}/{len(modules)}")
        logger.debug(f"Module task: {module_question[:50]}...")
        
        state = CodeState()
        attempts = 0
        whitelist = []
        blacklist = []
        correct_lists = []
        
        try:
            while state.errorstate != "pass" and attempts <= config.max_attempts:
                attempts += 1
                logger.info(f"Module {count} - Attempt {attempts}/{config.max_attempts}")
                
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'status',
                        'message': f"Module {count} - Attempt {attempts}/{config.max_attempts}"
                    })
                
                code_gen(
                    config.process_id, config.model, state, None, 
                    module_question, config.iscontext, config.isexecution,
                    config.isuserreq, config.usereq, whitelist, blacklist,
                    correct_lists, config.program_name, count, config.method_type,
                    config.device_type, config.os_type
                )
                
                compiler(state, config.device_type, config.os_type)
                state.to_json(state.iterations, count, config.program_name, config.process_id, config.method_type)
                
                if state.errorstate == "pass":
                    logger.info(f"Module {count} compilation successful")
                    if config.stream_handler:
                        config.stream_handler.add_to_stream({
                            'type': 'module_success',
                            'module': count,
                            'code': state.generation
                        })
                    sub_solutions.append(state.generation)
                    break
                else:
                    logger.warning(f"Module {count} compilation failed: {state.error}")
                    if config.stream_handler:
                        config.stream_handler.add_to_stream({
                            'type': 'module_error',
                            'module': count,
                            'error': state.error
                        })
            
            if state.errorstate != "pass":
                logger.error(f"Failed to generate working code for module {count} after {config.max_attempts} attempts")
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'error',
                        'message': f"Failed to generate working code for module {count} after {config.max_attempts} attempts"
                    })
                
        except Exception as e:
            logger.error(f"Error in code agent for module {count}: {str(e)}")
            if config.stream_handler:
                config.stream_handler.add_to_stream({
                    'type': 'error',
                    'message': f"Error in code agent for module {count}: {str(e)}"
                })
            
    logger.info(f"Generated {len(sub_solutions)}/{len(modules)} module solutions")
    return sub_solutions

def integration_agent(config: MultiAgentConfig, question: str, sub_solutions: List[str]) -> Optional[str]:
    """Integrate the individual module solutions into a complete application.
    
    Args:
        config: Configuration parameters for the agent
        question: The original programming task description
        sub_solutions: List of generated code solutions for each module
        
    Returns:
        Optional[str]: The integrated code if successful, None otherwise
    """
    if not sub_solutions:
        logger.warning("No module solutions to integrate")
        if config.stream_handler:
            config.stream_handler.add_to_stream({
                'type': 'error',
                'message': "No module solutions to integrate"
            })
        return None
        
    logger.info(f"Starting integration of {len(sub_solutions)} module solutions")
    if config.stream_handler:
        config.stream_handler.add_to_stream({
            'type': 'status',
            'message': f"Starting integration of {len(sub_solutions)} module solutions"
        })
    
    state = CodeState()
    attempts = 0
    
    try:
        while state.errorstate != "pass" and attempts <= config.max_attempts:
            attempts += 1
            logger.info(f"Integration attempt {attempts}/{config.max_attempts}")
            
            if config.stream_handler:
                config.stream_handler.add_to_stream({
                    'type': 'status',
                    'message': f"Integration attempt {attempts}/{config.max_attempts}"
                })
            
            intergration_gen(
                config.process_id, config.program_name, config.model,
                state, question, sub_solutions, config.iscontext, config.role
            )
            
            compiler(state, config.device_type, config.os_type)
            state.to_json(state.iterations, -1, config.program_name, config.process_id, config.method_type)
            
            if state.errorstate == "pass":
                logger.info("Integration successful")
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'integration_success',
                        'code': state.generation
                    })
                return state.generation
            else:
                logger.warning(f"Integration failed: {state.error}")
                if config.stream_handler:
                    config.stream_handler.add_to_stream({
                        'type': 'integration_error',
                        'error': state.error
                    })
                
        if state.errorstate != "pass":
            logger.error(f"Failed to integrate modules after {config.max_attempts} attempts")
            if config.stream_handler:
                config.stream_handler.add_to_stream({
                    'type': 'error',
                    'message': f"Failed to integrate modules after {config.max_attempts} attempts"
                })
            return None
            
    except Exception as e:
        logger.error(f"Integration agent failed: {str(e)}")
        if config.stream_handler:
            config.stream_handler.add_to_stream({
                'type': 'error',
                'message': f"Integration agent failed: {str(e)}"
            })
        return None
        
    return state.generation

def multi_agent(
    process_id: int,
    model: str,
    question: str,
    max_attempts: int,
    iscontext: bool,
    isexecution: bool,
    isruntime: bool,
    isuserreq: bool,
    usereq: str,
    program_name: str,
    role: int,
    method_type: str,
    device_type: str = "esp32",
    os_type: str = "RIOT",
    stream_handler: Optional[Any] = None
) -> Optional[str]:
    """Main entry point for multi-agent code generation and testing.
    
    This function implements the multi-agent approach for generating IoT code:
    1. Outline Agent: Breaks down the problem into smaller modules
    2. Code Agents: Generate code for each module independently
    3. Integration Agent: Combines the module solutions into a complete application
    
    Args:
        process_id: Unique identifier for the process
        model: Name of the model to use for code generation
        question: The programming task description
        max_attempts: Maximum number of attempts for compilation
        iscontext: Whether to use context-aware generation
        isexecution: Whether to use execution-aware generation
        isruntime: Whether to perform runtime testing
        isuserreq: Whether to consider user requirements
        usereq: User requirements specification
        program_name: Name of the program being generated
        role: Role identifier for the agent
        method_type: Type of method to use for code generation
        device_type: Target device type
        os_type: Target operating system type
        stream_handler: Optional handler for streaming updates
        
    Returns:
        Optional[str]: The generated code if successful, None otherwise
    """
    try:
        logger.info(f"Starting multi-agent process for: {program_name}")
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'status',
                'message': f"Starting multi-agent process for: {program_name}"
            })
        
        config = MultiAgentConfig(
            process_id=process_id,
            model=model,
            question=question,
            max_attempts=max_attempts,
            iscontext=iscontext,
            isexecution=isexecution,
            isruntime=isruntime,
            isuserreq=isuserreq,
            usereq=usereq,
            program_name=program_name,
            role=role,
            device_type=device_type,
            os_type=os_type,
            method_type=method_type,
            stream_handler=stream_handler
        )
        
        # Phase 1: Outline generation
        modules = outline_agent(model, question, process_id, stream_handler)
        if not modules:
            logger.error("Outline generation failed, aborting multi-agent process")
            return None
            
        # Phase 2: Module code generation
        sub_solutions = code_agents(config, modules)
        if not sub_solutions:
            logger.error("No module solutions generated, aborting integration")
            return None
            
        # Phase 3: Integration
        final_code = integration_agent(config, question, sub_solutions)
        
        if final_code and stream_handler:
            stream_handler.add_to_stream({
                'type': 'result',
                'data': final_code
            })
            
        return final_code
        
    except Exception as e:
        logger.error(f"Multi-agent process failed: {str(e)}")
        if stream_handler:
            stream_handler.add_to_stream({
                'type': 'error',
                'message': f"Multi-agent process failed: {str(e)}"
            })
        return None






        




