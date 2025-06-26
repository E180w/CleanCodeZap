"""
Utility functions for CleanCodeZap.
"""

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Set
import click


def print_success(message: str) -> None:
    """Print success message in green."""
    click.echo(click.style(message, fg='green'))


def print_error(message: str) -> None:
    """Print error message in red."""
    click.echo(click.style(message, fg='red'), err=True)


def print_info(message: str) -> None:
    """Print info message in blue."""
    click.echo(click.style(message, fg='blue'))


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    click.echo(click.style(message, fg='yellow'))


def validate_project_path(path: Path) -> bool:
    """
    Validate that the given path exists and is accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    try:
        return path.exists() and path.is_dir()
    except (OSError, PermissionError):
        return False


def detect_project_language(project_path: Path) -> Optional[str]:
    """
    Auto-detect the programming language of a project.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Detected language ('python', 'javascript', 'go') or None
    """
    # Language indicators
    indicators = {
        'python': [
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
            '*.py', '__pycache__', '.python-version'
        ],
        'javascript': [
            'package.json', 'package-lock.json', 'yarn.lock', 'node_modules',
            '*.js', '*.ts', '*.jsx', '*.tsx', '.nvmrc'
        ],
        'go': [
            'go.mod', 'go.sum', 'main.go', '*.go', 'vendor'
        ]
    }
    
    scores = {'python': 0, 'javascript': 0, 'go': 0}
    
    # Check for specific files and directories
    for item in project_path.rglob('*'):
        if item.is_file():
            for lang, patterns in indicators.items():
                for pattern in patterns:
                    if pattern.startswith('*.'):
                        # File extension check
                        if item.suffix == pattern[1:]:
                            scores[lang] += 1
                    elif item.name == pattern:
                        # Exact filename match
                        scores[lang] += 3
        elif item.is_dir():
            for lang, patterns in indicators.items():
                for pattern in patterns:
                    if item.name == pattern:
                        scores[lang] += 2
    
    # Return language with highest score
    if max(scores.values()) == 0:
        return None
    
    return max(scores, key=scores.get)


def find_files_by_extension(project_path: Path, extensions: List[str]) -> List[Path]:
    """
    Find all files with given extensions in the project.
    
    Args:
        project_path: Path to search in
        extensions: List of file extensions (e.g., ['.py', '.js'])
        
    Returns:
        List of file paths
    """
    files = []
    for ext in extensions:
        files.extend(project_path.rglob(f'*{ext}'))
    return files


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is binary, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\0' in chunk
    except (OSError, PermissionError):
        return True


def run_command(command: List[str], cwd: Optional[Path] = None) -> Dict[str, any]:
    """
    Run a shell command and return the result.
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory for the command
        
    Returns:
        Dictionary with 'success', 'stdout', 'stderr', 'returncode'
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def check_tool_availability(tool: str) -> bool:
    """
    Check if a command-line tool is available.
    
    Args:
        tool: Name of the tool to check
        
    Returns:
        True if tool is available, False otherwise
    """
    return shutil.which(tool) is not None


def extract_imports_from_python_file(file_path: Path) -> Set[str]:
    """
    Extract import statements from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Set of imported module names
    """
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match import statements
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module = match.group(1).split('.')[0]
                    imports.add(module)
    except (OSError, UnicodeDecodeError):
        pass
    
    return imports


def extract_requires_from_js_file(file_path: Path) -> Set[str]:
    """
    Extract require/import statements from a JavaScript/TypeScript file.
    
    Args:
        file_path: Path to the JS/TS file
        
    Returns:
        Set of required module names
    """
    requires = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match require and import statements
        patterns = [
            r'require\s*\(\s*[\'"]([^\'"\s]+)[\'"]\s*\)',
            r'import\s+.*?\s+from\s+[\'"]([^\'"\s]+)[\'"]',
            r'import\s+[\'"]([^\'"\s]+)[\'"]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Extract package name (before first slash)
                package = match.split('/')[0]
                if not package.startswith('.'):  # Skip relative imports
                    requires.add(package)
    except (OSError, UnicodeDecodeError):
        pass
    
    return requires


def extract_imports_from_go_file(file_path: Path) -> Set[str]:
    """
    Extract import statements from a Go file.
    
    Args:
        file_path: Path to the Go file
        
    Returns:
        Set of imported package names
    """
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match import statements
        patterns = [
            r'import\s+"([^"]+)"',
            r'import\s+\(\s*([^)]+)\s*\)',
        ]
        
        for pattern in patterns:
            if 'import (' in content:
                # Multi-line import block
                import_block = re.search(r'import\s+\(([^)]+)\)', content, re.DOTALL)
                if import_block:
                    lines = import_block.group(1).split('\n')
                    for line in lines:
                        line = line.strip()
                        match = re.search(r'"([^"]+)"', line)
                        if match:
                            package = match.group(1).split('/')[-1]
                            imports.add(package)
            else:
                # Single import lines
                matches = re.findall(r'import\s+"([^"]+)"', content)
                for match in matches:
                    package = match.split('/')[-1]
                    imports.add(package)
    except (OSError, UnicodeDecodeError):
        pass
    
    return imports


def backup_file(file_path: Path, backup_dir: Path) -> Path:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store the backup
        
    Returns:
        Path to the backup file
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create relative path structure in backup
    relative_path = file_path.relative_to(file_path.parent.parent)
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def create_gitignore_if_missing(project_path: Path, language: str) -> None:
    """
    Create a .gitignore file if it doesn't exist.
    
    Args:
        project_path: Path to the project
        language: Programming language of the project
    """
    gitignore_path = project_path / '.gitignore'
    if gitignore_path.exists():
        return
    
    templates = {
        'python': [
            '__pycache__/',
            '*.py[cod]',
            '*$py.class',
            '*.so',
            '.Python',
            'build/',
            'develop-eggs/',
            'dist/',
            'downloads/',
            'eggs/',
            '.eggs/',
            'lib/',
            'lib64/',
            'parts/',
            'sdist/',
            'var/',
            'wheels/',
            '*.egg-info/',
            '.installed.cfg',
            '*.egg',
            'MANIFEST',
            '.env',
            '.venv',
            'env/',
            'venv/',
            'ENV/',
            'env.bak/',
            'venv.bak/',
        ],
        'javascript': [
            'node_modules/',
            'npm-debug.log*',
            'yarn-debug.log*',
            'yarn-error.log*',
            '.npm',
            '.eslintcache',
            '.nyc_output',
            'coverage/',
            '.grunt',
            'bower_components',
            '.lock-wscript',
            'build/Release',
            '.node_repl_history',
            '*.tgz',
            '.yarn-integrity',
            '.env',
            '.env.local',
            '.env.development.local',
            '.env.test.local',
            '.env.production.local',
        ],
        'go': [
            '*.exe',
            '*.exe~',
            '*.dll',
            '*.so',
            '*.dylib',
            '*.test',
            '*.out',
            'go.work',
            'vendor/',
        ]
    }
    
    if language in templates:
        try:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(f"# {language.title()} .gitignore\n\n")
                for pattern in templates[language]:
                    f.write(f"{pattern}\n")
        except OSError:
            pass  # Ignore if we can't create the file 