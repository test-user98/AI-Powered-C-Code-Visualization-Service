import subprocess
import json
import os
import tempfile
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def __init__(self):
        pass
        
    def find_functions(self, code: str) -> List[str]:
        """Use ast-grep to find all function definitions in C code"""
        ast_grep_cmd = self._find_ast_grep()
        
        if not ast_grep_cmd:
            logger.info("ast-grep not found in any of the checked locations, using regex fallback for function detection")
            return self._fallback_function_extraction(code)

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:

                pattern = '$_ $FUNCNAME($_) { $$$ }'

                cmd = [
                    ast_grep_cmd, 'run',
                    '--pattern', pattern,
                    '--lang', 'c',
                    '--json',  # Ensure JSON output
                    temp_file
                ]

                logger.info(f"Running ast-grep command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0 and result.stdout.strip():
                    try:
                        # Parse ast-grep JSON output
                        # ast-grep returns a JSON array when using --json flag
                        matches = json.loads(result.stdout)

                        function_names = []
                        for match in matches:
                            # Extract function name from meta variables
                            if 'meta_variables' in match and '$FUNCNAME' in match['meta_variables']:
                                func_vars = match['meta_variables']['$FUNCNAME']
                                if isinstance(func_vars, list) and len(func_vars) > 0:
                                    func_name = func_vars[0].get('text', '')
                                elif isinstance(func_vars, dict):
                                    func_name = func_vars.get('text', '')
                                else:
                                    func_name = str(func_vars) if func_vars else ''

                                if func_name and func_name not in function_names:
                                    # Filter out keywords and invalid names
                                    if (not func_name.startswith('_') and
                                        func_name not in {
                                            'if', 'for', 'while', 'do', 'switch', 'case', 'default',
                                            'break', 'continue', 'return', 'goto', 'sizeof'
                                        }):
                                        function_names.append(func_name)

                        if function_names:
                            logger.info(f"ast-grep found {len(function_names)} functions: {function_names}")
                            return function_names
                        else:
                            logger.warning("ast-grep found no valid functions, using regex fallback")
                            return self._fallback_function_extraction(code)

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.warning(f"Failed to parse ast-grep JSON output: {e}")
                        logger.warning(f"ast-grep stdout: {result.stdout[:500]}")
                        return self._fallback_function_extraction(code)
                else:
                    logger.warning(f"ast-grep command failed (exit code {result.returncode})")
                    if result.stderr:
                        logger.warning(f"ast-grep stderr: {result.stderr[:500]}")
                    return self._fallback_function_extraction(code)

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f"Error in find_functions: {e}")
            return self._fallback_function_extraction(code)
    
    def _fallback_function_extraction(self, code: str) -> List[str]:
        """Simple regex-based function extraction"""
        pattern = r'^\s*(?:int|void|char|float|double)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.findall(pattern, code, re.MULTILINE)
        functions = list(set(matches))  # Remove duplicates
        return functions
    
    def generate_mermaid_diagram(self, code: str, function_name: str) -> str:
        try:
            logger.info(f"Generating mermaid diagram for function: {function_name} using AST traversal")

            # Try AST-based generation first, fallback to basic diagram
            try:
                return self._generate_mermaid_from_ast(code, function_name)
            except Exception as ast_error:
                logger.warning(f"AST-based generation failed for {function_name}: {ast_error}, using basic diagram")
                return self._generate_basic_mermaid(function_name)

        except Exception as e:
            logger.error(f"Error generating Mermaid diagram for {function_name}: {e}")
            return self._generate_basic_mermaid(function_name)
    
    def _extract_function_code(self, code: str, function_name: str) -> str:
        # Find the function definition
        pattern = rf'(\w+\s+)?{re.escape(function_name)}\s*\([^)]*\)\s*{{'
        match = re.search(pattern, code)
        
        if not match:
            return f"{function_name}() {{ /* Function not found */ }}"
        
        start_pos = match.start()
        
        # Find the matching closing brace
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_pos, len(code)):
            char = code[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return code[start_pos:i+1]
        
        return code[start_pos:]
    
    def _find_ast_grep(self) -> str:
        ast_grep_paths = [
            'ast-grep',  # System PATH
            './ast-grep',  # Current directory
            '/usr/local/bin/ast-grep',  # Common Linux/Mac location
            '/opt/homebrew/bin/ast-grep',  # Homebrew location
            '/usr/bin/ast-grep',  # Another common location
            '/opt/local/bin/ast-grep',  # MacPorts location
        ]

        for path in ast_grep_paths:
            try:
                test_result = subprocess.run([path, '--version'],
                                           capture_output=True, timeout=5)
                if test_result.returncode == 0:
                    logger.info(f"Found ast-grep at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        return None

    def _generate_mermaid_from_ast(self, code: str, function_name: str) -> str:
        """Generate Mermaid diagram by analyzing control structures using ast-grep patterns"""
        ast_grep_cmd = self._find_ast_grep()
        if not ast_grep_cmd:
            raise Exception("ast-grep not available for AST traversal")

        function_code = self._extract_function_code(code, function_name)
        if not function_code:
            raise Exception(f"Could not extract code for function {function_name}")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(function_code)
            temp_file = f.name

        try:
            # Get all control structures with their positions
            structures = self._analyze_control_structures_with_positions(function_code, ast_grep_cmd, temp_file)
            
            # Build diagram based on actual code flow
            return self._build_flowchart_from_structures(function_name, structures, function_code)

        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _analyze_control_structures_with_positions(self, function_code: str, ast_grep_cmd: str, temp_file: str) -> list:
        """Analyze function code for control structures with their positions using ast-grep"""
        structures = []

        try:
            # Use simpler patterns that ast-grep can match
            # Pattern for if statements
            if_pattern = 'if'
            result = subprocess.run(
                [ast_grep_cmd, 'run', '--pattern', if_pattern, '--lang', 'c', '--json', temp_file],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    matches = json.loads(result.stdout)
                    if isinstance(matches, list):
                        for match in matches:
                            # Get position from byteOffset or line/column
                            start = 0
                            if 'range' in match:
                                range_info = match['range']
                                if 'byteOffset' in range_info:
                                    start = range_info['byteOffset'].get('start', 0)
                                elif 'start' in range_info:
                                    start_info = range_info['start']
                                    if 'line' in start_info:
                                        # Use line number as approximate position
                                        line = start_info.get('line', 0)
                                        col = start_info.get('column', 0)
                                        start = line * 1000 + col  # Approximate
                            
                            # Check for else-if by looking at the code
                            code_snippet = function_code[start:start+500] if start < len(function_code) else ""
                            has_else = 'else' in code_snippet
                            is_else_if = 'else if' in code_snippet or 'elseif' in code_snippet
                            
                            structures.append({
                                'type': 'if',
                                'start': start,
                                'has_else': has_else and not is_else_if,
                                'is_else_if': is_else_if
                            })
                            logger.info(f"Found if statement at position {start}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse if pattern results: {e}")
                    logger.debug(f"ast-grep output: {result.stdout[:500]}")

            # Pattern for for loops
            for_pattern = 'for'
            result = subprocess.run(
                [ast_grep_cmd, 'run', '--pattern', for_pattern, '--lang', 'c', '--json', temp_file],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    matches = json.loads(result.stdout)
                    if isinstance(matches, list):
                        for match in matches:
                            start = 0
                            if 'range' in match:
                                range_info = match['range']
                                if 'byteOffset' in range_info:
                                    start = range_info['byteOffset'].get('start', 0)
                                elif 'start' in range_info:
                                    start_info = range_info['start']
                                    if 'line' in start_info:
                                        line = start_info.get('line', 0)
                                        col = start_info.get('column', 0)
                                        start = line * 1000 + col
                            structures.append({
                                'type': 'for',
                                'start': start
                            })
                            logger.info(f"Found for loop at position {start}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse for pattern results: {e}")
                    logger.debug(f"ast-grep output: {result.stdout[:500]}")

            # Pattern for while loops
            while_pattern = 'while'
            result = subprocess.run(
                [ast_grep_cmd, 'run', '--pattern', while_pattern, '--lang', 'c', '--json', temp_file],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    matches = json.loads(result.stdout)
                    if isinstance(matches, list):
                        for match in matches:
                            start = 0
                            if 'range' in match:
                                range_info = match['range']
                                if 'byteOffset' in range_info:
                                    start = range_info['byteOffset'].get('start', 0)
                                elif 'start' in range_info:
                                    start_info = range_info['start']
                                    if 'line' in start_info:
                                        line = start_info.get('line', 0)
                                        col = start_info.get('column', 0)
                                        start = line * 1000 + col
                            structures.append({
                                'type': 'while',
                                'start': start
                            })
                            logger.info(f"Found while loop at position {start}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse while pattern results: {e}")

            # Pattern for return statements
            return_pattern = 'return'
            result = subprocess.run(
                [ast_grep_cmd, 'run', '--pattern', return_pattern, '--lang', 'c', '--json', temp_file],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    matches = json.loads(result.stdout)
                    if isinstance(matches, list):
                        for match in matches:
                            start = 0
                            if 'range' in match:
                                range_info = match['range']
                                if 'byteOffset' in range_info:
                                    start = range_info['byteOffset'].get('start', 0)
                                elif 'start' in range_info:
                                    start_info = range_info['start']
                                    if 'line' in start_info:
                                        line = start_info.get('line', 0)
                                        col = start_info.get('column', 0)
                                        start = line * 1000 + col
                            structures.append({
                                'type': 'return',
                                'start': start
                            })
                            logger.info(f"Found return statement at position {start}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse return pattern results: {e}")

        except Exception as e:
            logger.error(f"Error analyzing control structures: {e}")

        # Sort by position in code
        structures.sort(key=lambda x: x.get('start', 0))
        logger.info(f"Found {len(structures)} control structures: {[s['type'] for s in structures]}")
        return structures

    def _build_flowchart_from_structures(self, function_name: str, structures: list, function_code: str) -> str:
        """Build Mermaid flowchart from detected structures, handling nesting"""
        diagram_lines = ["flowchart TD"]
        diagram_lines.append(f"    START([{function_name}])")
        
        if not structures:
            # Check if function has return statement
            if 'return' in function_code.lower():
                diagram_lines.append("    START --> RETURN[Return]")
                diagram_lines.append("    RETURN --> END([End])")
            else:
                diagram_lines.append("    START --> END([End])")
            return "\n".join(diagram_lines)

        # Build nodes and connections
        node_id = 0
        current_node = "START"
        
        for struct in structures:
            struct_type = struct['type']
            
            if struct_type == 'for':
                loop_node = f"FOR{node_id}"
                body_node = f"FORBODY{node_id}"
                exit_node = f"FOREXIT{node_id}"
                
                diagram_lines.append(f"    {current_node} --> {loop_node}{{For Loop}}")
                diagram_lines.append(f"    {loop_node} -->|True| {body_node}[Loop Body]")
                diagram_lines.append(f"    {body_node} --> {loop_node}")
                diagram_lines.append(f"    {loop_node} -->|False| {exit_node}[Continue]")
                
                current_node = body_node
                node_id += 1
                
            elif struct_type == 'while':
                loop_node = f"WHILE{node_id}"
                body_node = f"WHILEBODY{node_id}"
                exit_node = f"WHILEEXIT{node_id}"
                
                diagram_lines.append(f"    {current_node} --> {loop_node}{{While}}")
                diagram_lines.append(f"    {loop_node} -->|True| {body_node}[Body]")
                diagram_lines.append(f"    {body_node} --> {loop_node}")
                diagram_lines.append(f"    {loop_node} -->|False| {exit_node}[Continue]")
                
                current_node = body_node
                node_id += 1
                
            elif struct_type == 'if':
                if_node = f"IF{node_id}"
                then_node = f"THEN{node_id}"
                else_node = f"ELSE{node_id}"
                merge_node = f"MERGE{node_id}"
                
                has_else = struct.get('has_else', False)
                
                diagram_lines.append(f"    {current_node} --> {if_node}{{If}}")
                diagram_lines.append(f"    {if_node} -->|Yes| {then_node}[Then]")
                
                if has_else:
                    diagram_lines.append(f"    {if_node} -->|No| {else_node}[Else]")
                    diagram_lines.append(f"    {then_node} --> {merge_node}[Continue]")
                    diagram_lines.append(f"    {else_node} --> {merge_node}")
                else:
                    diagram_lines.append(f"    {if_node} -->|No| {merge_node}[Continue]")
                    diagram_lines.append(f"    {then_node} --> {merge_node}")
                
                current_node = merge_node
                node_id += 1
                
            elif struct_type == 'return':
                return_node = f"RETURN{node_id}"
                diagram_lines.append(f"    {current_node} --> {return_node}[Return]")
                diagram_lines.append(f"    {return_node} --> END([End])")
                return "\n".join(diagram_lines)

        # Connect to end
        diagram_lines.append(f"    {current_node} --> END([End])")
        return "\n".join(diagram_lines)

    def _generate_basic_mermaid(self, function_name: str) -> str:
        """Generate a basic Mermaid diagram as fallback"""
        return f"""flowchart TD
    A[{function_name}] --> B[Process]
    B --> C[Return]"""
    
