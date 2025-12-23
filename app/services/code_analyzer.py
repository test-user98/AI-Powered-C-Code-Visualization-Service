import subprocess
import json
import os
import tempfile
import re
from typing import List, Optional
import openai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    # Ignore dotenv loading errors in sandboxed environments
    logger.warning(f"Could not load .env file: {e}")

class CodeAnalyzer:
    def __init__(self):
        try:
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except TypeError as e:
            if "proxies" in str(e):
                import httpx
                http_client = httpx.Client()
                self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
            else:
                raise e
        
    def find_functions(self, code: str) -> List[str]:
        """Use ast-grep to find all function definitions in C code"""
        # Check for ast-grep in multiple locations
        ast_grep_paths = [
            'ast-grep',  # System PATH
            './ast-grep',  # Current directory
            '/usr/local/bin/ast-grep',  # Common Linux/Mac location
            '/opt/homebrew/bin/ast-grep',  # Homebrew location
            '/usr/bin/ast-grep',  # Another common location
            '/opt/local/bin/ast-grep',  # MacPorts location
        ]

        ast_grep_cmd = None
        for path in ast_grep_paths:
            try:
                # Test if ast-grep is available at this path
                test_result = subprocess.run([path, '--version'],
                                           capture_output=True, timeout=5)
                if test_result.returncode == 0:
                    ast_grep_cmd = path
                    logger.info(f"Found ast-grep at: {path}")
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        if not ast_grep_cmd:
            logger.info("ast-grep not found in any of the checked locations, using regex fallback for function detection")
            return self._fallback_function_extraction(code)

        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Simple and reliable pattern for C function declarations
                # Pattern: return_type function_name(parameters) { ... }
                # Using ast-grep's pattern syntax
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
        # Simple pattern: return_type function_name(parameters) {
        pattern = r'^\s*(?:int|void|char|float|double)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.findall(pattern, code, re.MULTILINE)
        functions = list(set(matches))  # Remove duplicates
        return functions
    
    def generate_mermaid_diagram(self, code: str, function_name: str) -> str:
        """Generate a Mermaid flowchart for a specific function using AST traversal"""
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
        """Extract a specific function's code from the full source"""
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
    
    def _generate_mermaid_from_ast(self, code: str, function_name: str) -> str:
        """Generate Mermaid diagram by analyzing control structures using ast-grep patterns"""
        ast_grep_cmd = self._find_ast_grep()
        if not ast_grep_cmd:
            raise Exception("ast-grep not available for AST traversal")

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Extract function code first
            function_code = self._extract_function_code(code, function_name)
            if not function_code:
                raise Exception(f"Could not extract code for function {function_name}")

            # Build Mermaid diagram by analyzing different control structures
            diagram_lines = [f"flowchart TD"]

            # Start with function entry
            diagram_lines.append(f"    START([{function_name} starts])")

            # Find and process different control structures
            structures = self._analyze_control_structures(function_code, ast_grep_cmd, temp_file)

            if structures:
                # Build the flow based on found structures
                current_node = "START"
                node_counter = 0

                for struct_type, details in structures:
                    if struct_type == 'if':
                        current_node, node_counter = self._add_if_node(diagram_lines, current_node, node_counter, details)
                    elif struct_type == 'for':
                        current_node, node_counter = self._add_for_node(diagram_lines, current_node, node_counter, details)
                    elif struct_type == 'while':
                        current_node, node_counter = self._add_while_node(diagram_lines, current_node, node_counter, details)
                    elif struct_type == 'return':
                        current_node, node_counter = self._add_return_node(diagram_lines, current_node, node_counter, details)

                # Connect to end
                diagram_lines.append(f"    {current_node} --> END([{function_name} ends])")
            else:
                # Simple function with no control structures
                diagram_lines.append("    START --> PROCESS[Process]")
                diagram_lines.append("    PROCESS --> END([Function ends])")

            return "\n".join(diagram_lines)

        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _analyze_control_structures(self, function_code: str, ast_grep_cmd: str, temp_file: str) -> list:
        """Analyze function code for control structures using ast-grep patterns"""
        structures = []

        # Create a temporary file with just the function code for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as func_file:
            func_file.write(function_code)
            func_temp_file = func_file.name

        try:
            # Pattern for if statements
            if_pattern = 'if ($CONDITION) $BODY'
            result = subprocess.run([ast_grep_cmd, 'run', '--pattern', if_pattern, '--lang', 'c', '--json', func_temp_file],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                try:
                    matches = json.loads(result.stdout)
                    structures.extend([('if', {'condition': 'if condition'}) for _ in matches])
                except:
                    pass

            # Pattern for for loops
            for_pattern = 'for ($INIT; $COND; $UPDATE) $BODY'
            result = subprocess.run([ast_grep_cmd, 'run', '--pattern', for_pattern, '--lang', 'c', '--json', func_temp_file],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                try:
                    matches = json.loads(result.stdout)
                    structures.extend([('for', {'type': 'for loop'}) for _ in matches])
                except:
                    pass

            # Pattern for while loops
            while_pattern = 'while ($CONDITION) $BODY'
            result = subprocess.run([ast_grep_cmd, 'run', '--pattern', while_pattern, '--lang', 'c', '--json', func_temp_file],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                try:
                    matches = json.loads(result.stdout)
                    structures.extend([('while', {'type': 'while loop'}) for _ in matches])
                except:
                    pass

            # Pattern for return statements
            return_pattern = 'return $EXPR;'
            result = subprocess.run([ast_grep_cmd, 'run', '--pattern', return_pattern, '--lang', 'c', '--json', func_temp_file],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                try:
                    matches = json.loads(result.stdout)
                    structures.extend([('return', {'type': 'return'}) for _ in matches])
                except:
                    pass

        finally:
            try:
                os.unlink(func_temp_file)
            except OSError:
                pass

        return structures

    def _add_if_node(self, lines: list, prev_node: str, node_counter: int, details: dict) -> tuple:
        """Add if-statement node to diagram"""
        decision_node = f"N{node_counter}"
        lines.append(f"    {prev_node} --> {decision_node}{{If condition}}")
        node_counter += 1

        # Then branch
        then_node = f"N{node_counter}"
        lines.append(f"    {decision_node} -->|Yes| {then_node}[Then branch]")
        node_counter += 1

        # Merge point
        merge_node = f"N{node_counter}"
        lines.append(f"    {decision_node} --> {merge_node}[Continue]")
        node_counter += 1

        return merge_node, node_counter

    def _add_for_node(self, lines: list, prev_node: str, node_counter: int, details: dict) -> tuple:
        """Add for-loop node to diagram"""
        loop_node = f"N{node_counter}"
        lines.append(f"    {prev_node} --> {loop_node}{{For loop}}")
        node_counter += 1

        # Loop body
        body_node = f"N{node_counter}"
        lines.append(f"    {loop_node} -->|Continue| {body_node}[Loop body]")
        node_counter += 1

        # Loop back
        lines.append(f"    {body_node} --> {loop_node}")

        # Exit
        exit_node = f"N{node_counter}"
        lines.append(f"    {loop_node} -->|Exit| {exit_node}[Continue]")
        node_counter += 1

        return exit_node, node_counter

    def _add_while_node(self, lines: list, prev_node: str, node_counter: int, details: dict) -> tuple:
        """Add while-loop node to diagram"""
        loop_node = f"N{node_counter}"
        lines.append(f"    {prev_node} --> {loop_node}{{While condition}}")
        node_counter += 1

        # Loop body
        body_node = f"N{node_counter}"
        lines.append(f"    {loop_node} -->|True| {body_node}[Loop body]")
        node_counter += 1

        # Loop back
        lines.append(f"    {body_node} --> {loop_node}")

        # Exit
        exit_node = f"N{node_counter}"
        lines.append(f"    {loop_node} -->|False| {exit_node}[Continue]")
        node_counter += 1

        return exit_node, node_counter

    def _add_return_node(self, lines: list, prev_node: str, node_counter: int, details: dict) -> tuple:
        """Add return statement node to diagram"""
        return_node = f"N{node_counter}"
        lines.append(f"    {prev_node} --> {return_node}[Return]")
        node_counter += 1

        # End node
        end_node = f"N{node_counter}"
        lines.append(f"    {return_node} --> {end_node}[Function ends]")
        node_counter += 1

        return end_node, node_counter

    def _find_ast_grep(self) -> str:
        """Find ast-grep executable"""
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
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        return None

    def _generate_basic_mermaid(self, function_name: str) -> str:
        """Generate a basic Mermaid diagram as fallback"""
        return f"""flowchart TD
    A[{function_name}] --> B[Process]
    B --> C[Return]"""
    
    def validate_mermaid_syntax(self, mermaid_code: str) -> bool:
        """Validate Mermaid syntax using mermaid-cli"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_code)
                temp_file = f.name
            
            try:
                # Use mermaid-cli to validate via npx (no global installation needed)
                cmd = ['npx', '--yes', '@mermaid-js/mermaid-cli@latest', '--input', temp_file, '--output', '/dev/null', '--configFile', '/dev/null']

                result = subprocess.run(cmd, capture_output=True, timeout=10)
                
                # mmdc returns 0 on success, non-zero on error
                return result.returncode == 0
                
            except FileNotFoundError:
                # mermaid-cli not available, do basic validation
                logger.warning("mermaid-cli not available, using basic validation")
                return self._basic_mermaid_validation(mermaid_code)
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Error validating Mermaid syntax: {e}")
            return False
    
    def _basic_mermaid_validation(self, mermaid_code: str) -> bool:
        """Basic Mermaid syntax validation"""
        lines = mermaid_code.strip().split('\n')
        if not lines:
            return False
        
        # Check if it starts with flowchart
        if not lines[0].startswith('flowchart'):
            return False
        
        # Basic structure check
        has_connections = False
        for line in lines[1:]:
            line = line.strip()
            if '-->' in line or '---' in line:
                has_connections = True
                break
        
        return has_connections
    
    def fix_mermaid_diagram(self, mermaid_code: str) -> str:
        """Try to fix invalid Mermaid syntax using LLM"""
        try:
            prompt = f"""The following Mermaid diagram has syntax errors. Please fix them and return a valid Mermaid flowchart:

```
{mermaid_code}
```

Return ONLY the corrected Mermaid syntax, no explanations."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at fixing Mermaid diagram syntax errors."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            fixed_code = response.choices[0].message.content.strip()
            fixed_code = re.sub(r'```mermaid\s*', '', fixed_code)
            fixed_code = re.sub(r'```\s*$', '', fixed_code)
            
            return fixed_code.strip()
            
        except Exception as e:
            logger.error(f"Error fixing Mermaid diagram: {e}")
            return mermaid_code
