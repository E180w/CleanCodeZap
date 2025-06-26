"""
Core functionality for CleanCodeZap.
"""

import os
import re
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime

from .utils import (
    find_files_by_extension,
    is_binary_file,
    run_command,
    check_tool_availability,
    extract_imports_from_python_file,
    extract_requires_from_js_file,
    extract_imports_from_go_file,
    backup_file,
    create_gitignore_if_missing
)


class CodeCleaner:
    """
    Main class for cleaning and optimizing code projects.
    """
    
    def __init__(self, project_path: Path, language: str):
        """
        Initialize the code cleaner.
        
        Args:
            project_path: Path to the project directory
            language: Programming language ('python', 'javascript', 'go')
        """
        self.project_path = project_path
        self.language = language
        self.backup_dir = None
        
        # Language-specific configurations
        self.config = {
            'python': {
                'extensions': ['.py'],
                'dependency_files': ['requirements.txt', 'setup.py', 'pyproject.toml'],
                'formatter': 'black',
                'cleaner': 'autoflake'
            },
            'javascript': {
                'extensions': ['.js', '.ts', '.jsx', '.tsx'],
                'dependency_files': ['package.json'],
                'formatter': 'prettier',
                'cleaner': 'eslint'
            },
            'go': {
                'extensions': ['.go'],
                'dependency_files': ['go.mod'],
                'formatter': 'gofmt',
                'cleaner': 'go'
            }
        }
    
    def analyze(self) -> List[str]:
        """
        Analyze the project and return a list of issues found.
        
        Returns:
            List of issue descriptions
        """
        issues = []
        
        # Find code files
        files = self._get_code_files()
        if not files:
            issues.append("No project files found, check the path")
            return issues
        
        # Check for unused imports
        unused_imports = self._find_unused_imports(files)
        if unused_imports:
            issues.append(f"Found {len(unused_imports)} files with unused imports")
        
        # Check for commented code
        commented_code = self._find_commented_code(files)
        if commented_code:
            issues.append(f"Found {len(commented_code)} files with commented-out code")
        
        # Check for formatting issues
        formatting_issues = self._check_formatting(files)
        if formatting_issues:
            issues.append(f"Found {len(formatting_issues)} files with formatting issues")
        
        # Check dependencies
        dependency_issues = self._check_dependencies()
        if dependency_issues['unused']:
            issues.append(f"Found {len(dependency_issues['unused'])} unused dependencies")
        if dependency_issues['outdated']:
            issues.append(f"Found {len(dependency_issues['outdated'])} outdated dependencies")
        
        return issues
    
    def clean(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Clean the project by removing unused code and optimizing.
        
        Args:
            aggressive: Whether to perform aggressive cleaning
            
        Returns:
            Dictionary with cleaning results
        """
        results = {
            'files_processed': 0,
            'unused_imports_removed': 0,
            'unused_variables_removed': 0,
            'comments_removed': 0,
            'dependencies_cleaned': 0
        }
        
        files = self._get_code_files()
        if not files:
            return results
        
        for file_path in files:
            if self._clean_file(file_path, aggressive):
                results['files_processed'] += 1
        
        # Clean dependencies if requested
        if aggressive:
            dep_results = self.analyze_dependencies(remove_unused=True)
            results['dependencies_cleaned'] = len(dep_results.get('unused_dependencies', []))
        
        # Update results with detailed counts
        results.update(self._get_cleaning_stats(files))
        
        return results
    
    def format_code(self) -> Dict[str, Any]:
        """
        Format code according to language standards.
        
        Returns:
            Dictionary with formatting results
        """
        results = {'files_formatted': 0}
        
        files = self._get_code_files()
        if not files:
            return results
        
        formatter = self.config[self.language]['formatter']
        
        if self.language == 'python' and check_tool_availability('black'):
            result = run_command(['black', '--check', '--diff', str(self.project_path)])
            if not result['success']:
                # Format the files
                run_command(['black', str(self.project_path)])
                results['files_formatted'] = len(files)
        
        elif self.language == 'javascript' and check_tool_availability('prettier'):
            for file_path in files:
                result = run_command(['prettier', '--check', str(file_path)])
                if not result['success']:
                    run_command(['prettier', '--write', str(file_path)])
                    results['files_formatted'] += 1
        
        elif self.language == 'go' and check_tool_availability('gofmt'):
            for file_path in files:
                result = run_command(['gofmt', '-l', str(file_path)])
                if result['stdout'].strip():
                    run_command(['gofmt', '-w', str(file_path)])
                    results['files_formatted'] += 1
        
        return results
    
    def analyze_dependencies(self, remove_unused: bool = False) -> Dict[str, Any]:
        """
        Analyze project dependencies.
        
        Args:
            remove_unused: Whether to remove unused dependencies
            
        Returns:
            Dictionary with dependency analysis results
        """
        results = {
            'unused_dependencies': [],
            'outdated_dependencies': {},
            'dependency_file': None
        }
        
        dep_file = self._find_dependency_file()
        if not dep_file:
            return results
        
        results['dependency_file'] = str(dep_file)
        
        if self.language == 'python':
            results.update(self._analyze_python_dependencies(dep_file, remove_unused))
        elif self.language == 'javascript':
            results.update(self._analyze_js_dependencies(dep_file, remove_unused))
        elif self.language == 'go':
            results.update(self._analyze_go_dependencies(dep_file, remove_unused))
        
        return results
    
    def create_backup(self) -> Path:
        """
        Create a backup of the project.
        
        Returns:
            Path to the backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_path.parent / f"backup_{self.project_path.name}_{timestamp}"
        
        # Copy the entire project
        shutil.copytree(self.project_path, self.backup_dir, ignore=shutil.ignore_patterns(
            '__pycache__', 'node_modules', '.git', '*.pyc', '*.pyo'
        ))
        
        return self.backup_dir
    
    def _get_code_files(self) -> List[Path]:
        """Get list of code files in the project."""
        extensions = self.config[self.language]['extensions']
        files = find_files_by_extension(self.project_path, extensions)
        
        # Filter out binary files and files in ignored directories
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', '.venv'}
        
        filtered_files = []
        for file_path in files:
            # Check if file is in an ignored directory
            if any(ignored_dir in file_path.parts for ignored_dir in ignored_dirs):
                continue
            
            # Check if file is binary
            if is_binary_file(file_path):
                continue
            
            filtered_files.append(file_path)
        
        return filtered_files
    
    def _find_unused_imports(self, files: List[Path]) -> List[Path]:
        """Find files with unused imports."""
        files_with_unused = []
        
        for file_path in files:
            if self.language == 'python':
                # Use autoflake to check for unused imports
                if check_tool_availability('autoflake'):
                    result = run_command([
                        'autoflake', '--check', '--remove-unused-variables',
                        '--remove-all-unused-imports', str(file_path)
                    ])
                    if not result['success'] and 'would be reformatted' in result['stderr']:
                        files_with_unused.append(file_path)
        
        return files_with_unused
    
    def _find_commented_code(self, files: List[Path]) -> List[Path]:
        """Find files with commented-out code."""
        files_with_comments = []
        
        comment_patterns = {
            'python': r'^\s*#\s*[a-zA-Z_].*[=\(\)\[\]{}]',
            'javascript': r'^\s*//\s*[a-zA-Z_].*[=\(\)\[\]{}]',
            'go': r'^\s*//\s*[a-zA-Z_].*[=\(\)\[\]{}]'
        }
        
        pattern = comment_patterns.get(self.language)
        if not pattern:
            return files_with_comments
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                commented_lines = 0
                for line in content.split('\n'):
                    if re.match(pattern, line):
                        commented_lines += 1
                
                if commented_lines > 2:  # Threshold for commented code
                    files_with_comments.append(file_path)
            except (OSError, UnicodeDecodeError):
                continue
        
        return files_with_comments
    
    def _check_formatting(self, files: List[Path]) -> List[Path]:
        """Check files for formatting issues."""
        files_with_issues = []
        
        for file_path in files:
            if self.language == 'python' and check_tool_availability('black'):
                result = run_command(['black', '--check', str(file_path)])
                if not result['success']:
                    files_with_issues.append(file_path)
            
            elif self.language == 'javascript' and check_tool_availability('prettier'):
                result = run_command(['prettier', '--check', str(file_path)])
                if not result['success']:
                    files_with_issues.append(file_path)
            
            elif self.language == 'go' and check_tool_availability('gofmt'):
                result = run_command(['gofmt', '-l', str(file_path)])
                if result['stdout'].strip():
                    files_with_issues.append(file_path)
        
        return files_with_issues
    
    def _check_dependencies(self) -> Dict[str, List]:
        """Check for dependency issues."""
        result = {'unused': [], 'outdated': []}
        
        dep_file = self._find_dependency_file()
        if not dep_file:
            return result
        
        # This is a simplified check - in practice, you'd want more sophisticated analysis
        if self.language == 'python':
            result.update(self._check_python_dependencies(dep_file))
        elif self.language == 'javascript':
            result.update(self._check_js_dependencies(dep_file))
        elif self.language == 'go':
            result.update(self._check_go_dependencies(dep_file))
        
        return result
    
    def _clean_file(self, file_path: Path, aggressive: bool) -> bool:
        """Clean a single file."""
        try:
            if self.language == 'python':
                return self._clean_python_file(file_path, aggressive)
            elif self.language == 'javascript':
                return self._clean_js_file(file_path, aggressive)
            elif self.language == 'go':
                return self._clean_go_file(file_path, aggressive)
        except Exception:
            return False
        
        return False
    
    def _clean_python_file(self, file_path: Path, aggressive: bool) -> bool:
        """Clean a Python file."""
        if not check_tool_availability('autoflake'):
            return False
        
        command = [
            'autoflake',
            '--in-place',
            '--remove-unused-variables',
            '--remove-all-unused-imports'
        ]
        
        if aggressive:
            command.append('--remove-duplicate-keys')
        
        command.append(str(file_path))
        
        result = run_command(command)
        return result['success']
    
    def _clean_js_file(self, file_path: Path, aggressive: bool) -> bool:
        """Clean a JavaScript/TypeScript file."""
        # For JS, we'd typically use ESLint with --fix
        if not check_tool_availability('eslint'):
            return False
        
        result = run_command(['eslint', '--fix', str(file_path)])
        return result['success'] or result['returncode'] == 1  # ESLint returns 1 for fixable issues
    
    def _clean_go_file(self, file_path: Path, aggressive: bool) -> bool:
        """Clean a Go file."""
        # Go has built-in tools
        if not check_tool_availability('goimports'):
            return False
        
        result = run_command(['goimports', '-w', str(file_path)])
        return result['success']
    
    def _find_dependency_file(self) -> Optional[Path]:
        """Find the dependency file for the project."""
        dep_files = self.config[self.language]['dependency_files']
        
        for dep_file in dep_files:
            file_path = self.project_path / dep_file
            if file_path.exists():
                return file_path
        
        return None
    
    def _analyze_python_dependencies(self, dep_file: Path, remove_unused: bool) -> Dict[str, Any]:
        """Analyze Python dependencies."""
        result = {'unused_dependencies': [], 'outdated_dependencies': {}}
        
        # Read requirements.txt
        try:
            with open(dep_file, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except OSError:
            return result
        
        # Get used imports from all Python files
        files = self._get_code_files()
        used_imports = set()
        for file_path in files:
            used_imports.update(extract_imports_from_python_file(file_path))
        
        # Check which requirements are unused
        for req in requirements:
            package_name = re.split('[>=<]', req)[0].strip()
            if package_name and package_name not in used_imports:
                result['unused_dependencies'].append(package_name)
        
        # Remove unused dependencies if requested
        if remove_unused and result['unused_dependencies']:
            self._remove_unused_python_deps(dep_file, result['unused_dependencies'])
        
        return result
    
    def _analyze_js_dependencies(self, dep_file: Path, remove_unused: bool) -> Dict[str, Any]:
        """Analyze JavaScript dependencies."""
        result = {'unused_dependencies': [], 'outdated_dependencies': {}}
        
        try:
            with open(dep_file, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return result
        
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}
        
        # Get used requires from all JS files
        files = self._get_code_files()
        used_requires = set()
        for file_path in files:
            used_requires.update(extract_requires_from_js_file(file_path))
        
        # Check which dependencies are unused
        for dep_name in all_deps:
            if dep_name not in used_requires:
                result['unused_dependencies'].append(dep_name)
        
        return result
    
    def _analyze_go_dependencies(self, dep_file: Path, remove_unused: bool) -> Dict[str, Any]:
        """Analyze Go dependencies."""
        result = {'unused_dependencies': [], 'outdated_dependencies': {}}
        
        # Use go mod tidy to clean up
        if remove_unused and check_tool_availability('go'):
            run_command(['go', 'mod', 'tidy'], cwd=self.project_path)
        
        return result
    
    def _check_python_dependencies(self, dep_file: Path) -> Dict[str, List]:
        """Check Python dependencies for issues."""
        return {'unused': [], 'outdated': []}
    
    def _check_js_dependencies(self, dep_file: Path) -> Dict[str, List]:
        """Check JavaScript dependencies for issues."""
        return {'unused': [], 'outdated': []}
    
    def _check_go_dependencies(self, dep_file: Path) -> Dict[str, List]:
        """Check Go dependencies for issues."""
        return {'unused': [], 'outdated': []}
    
    def _remove_unused_python_deps(self, dep_file: Path, unused_deps: List[str]) -> None:
        """Remove unused Python dependencies."""
        try:
            with open(dep_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            filtered_lines = []
            for line in lines:
                package_name = re.split('[>=<]', line.strip())[0].strip()
                if package_name not in unused_deps:
                    filtered_lines.append(line)
            
            with open(dep_file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
        except OSError:
            pass
    
    def _get_cleaning_stats(self, files: List[Path]) -> Dict[str, int]:
        """Get detailed cleaning statistics."""
        return {
            'unused_imports_removed': 0,
            'unused_variables_removed': 0,
            'comments_removed': 0
        }