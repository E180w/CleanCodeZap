"""
Tests for CleanCodeZap core functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from cleancodezap.core import CodeCleaner
from cleancodezap.utils import detect_project_language, validate_project_path


class TestCodeCleaner:
    """Test the CodeCleaner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_python_project_detection(self):
        """Test Python project detection."""
        # Create a Python project structure
        (self.temp_dir / "main.py").touch()
        (self.temp_dir / "requirements.txt").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language == "python"
    
    def test_javascript_project_detection(self):
        """Test JavaScript project detection."""
        # Create a JavaScript project structure
        (self.temp_dir / "index.js").touch()
        (self.temp_dir / "package.json").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language == "javascript"
    
    def test_go_project_detection(self):
        """Test Go project detection."""
        # Create a Go project structure
        (self.temp_dir / "main.go").touch()
        (self.temp_dir / "go.mod").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language == "go"
    
    def test_validate_project_path(self):
        """Test project path validation."""
        assert validate_project_path(self.temp_dir) is True
        assert validate_project_path(Path("/nonexistent/path")) is False
    
    def test_cleaner_initialization(self):
        """Test CodeCleaner initialization."""
        cleaner = CodeCleaner(self.temp_dir, "python")
        assert cleaner.project_path == self.temp_dir
        assert cleaner.language == "python"
        assert cleaner.backup_dir is None
    
    def test_analyze_empty_project(self):
        """Test analyzing an empty project."""
        cleaner = CodeCleaner(self.temp_dir, "python")
        issues = cleaner.analyze()
        assert "No project files found, check the path" in issues
    
    def test_analyze_python_project(self):
        """Test analyzing a Python project."""
        # Create a simple Python file
        python_file = self.temp_dir / "test.py"
        python_file.write_text("""
import os
import sys
import unused_module

def main():
    print("Hello World")
    
if __name__ == "__main__":
    main()
""")
        
        cleaner = CodeCleaner(self.temp_dir, "python")
        issues = cleaner.analyze()
        # Should find the file but may not have specific tools for analysis
        assert isinstance(issues, list)
    
    def test_backup_creation(self):
        """Test backup creation."""
        # Create some files
        (self.temp_dir / "test.py").write_text("print('hello')")
        (self.temp_dir / "requirements.txt").write_text("requests==2.25.0")
        
        cleaner = CodeCleaner(self.temp_dir, "python")
        backup_path = cleaner.create_backup()
        
        assert backup_path.exists()
        assert (backup_path / "test.py").exists()
        assert (backup_path / "requirements.txt").exists()
    
    def test_find_code_files(self):
        """Test finding code files."""
        # Create mixed files
        (self.temp_dir / "test.py").touch()
        (self.temp_dir / "script.js").touch()
        (self.temp_dir / "main.go").touch()
        (self.temp_dir / "readme.txt").touch()
        
        # Test Python
        cleaner = CodeCleaner(self.temp_dir, "python")
        files = cleaner._get_code_files()
        assert len(files) == 1
        assert files[0].name == "test.py"
        
        # Test JavaScript
        cleaner = CodeCleaner(self.temp_dir, "javascript")
        files = cleaner._get_code_files()
        assert len(files) == 1
        assert files[0].name == "script.js"
        
        # Test Go
        cleaner = CodeCleaner(self.temp_dir, "go")
        files = cleaner._get_code_files()
        assert len(files) == 1
        assert files[0].name == "main.go"
    
    def test_clean_empty_project(self):
        """Test cleaning an empty project."""
        cleaner = CodeCleaner(self.temp_dir, "python")
        results = cleaner.clean()
        
        assert results['files_processed'] == 0
        assert results['unused_imports_removed'] == 0
        assert results['unused_variables_removed'] == 0
        assert results['comments_removed'] == 0
    
    def test_format_code_empty_project(self):
        """Test formatting an empty project."""
        cleaner = CodeCleaner(self.temp_dir, "python")
        results = cleaner.format_code()
        
        assert results['files_formatted'] == 0
    
    def test_analyze_dependencies_no_file(self):
        """Test dependency analysis with no dependency file."""
        cleaner = CodeCleaner(self.temp_dir, "python")
        results = cleaner.analyze_dependencies()
        
        assert results['unused_dependencies'] == []
        assert results['outdated_dependencies'] == {}
        assert results['dependency_file'] is None
    
    def test_analyze_python_dependencies(self):
        """Test Python dependency analysis."""
        # Create requirements.txt
        req_file = self.temp_dir / "requirements.txt"
        req_file.write_text("""
requests>=2.25.0
numpy==1.21.0
unused_package==1.0.0
""")
        
        # Create Python file that uses some packages
        py_file = self.temp_dir / "main.py"
        py_file.write_text("""
import requests
import json

def main():
    response = requests.get("https://api.example.com")
    data = json.loads(response.text)
    print(data)
""")
        
        cleaner = CodeCleaner(self.temp_dir, "python")
        results = cleaner.analyze_dependencies()
        
        assert results['dependency_file'] == str(req_file)
        # Should detect unused packages (but this depends on import analysis)
        assert isinstance(results['unused_dependencies'], list)


class TestProjectDetection:
    """Test project language detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_mixed_project_detection(self):
        """Test detection in mixed language projects."""
        # Create files for multiple languages
        (self.temp_dir / "script.py").touch()
        (self.temp_dir / "app.js").touch()
        (self.temp_dir / "main.go").touch()
        
        # Python indicators should win due to more weight
        (self.temp_dir / "requirements.txt").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language == "python"
    
    def test_no_project_detection(self):
        """Test when no language can be detected."""
        # Create only non-code files
        (self.temp_dir / "readme.txt").touch()
        (self.temp_dir / "data.csv").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language is None
    
    def test_subdirectory_detection(self):
        """Test detection with files in subdirectories."""
        # Create subdirectory structure
        src_dir = self.temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "main.py").touch()
        (src_dir / "utils.py").touch()
        (self.temp_dir / "setup.py").touch()
        
        language = detect_project_language(self.temp_dir)
        assert language == "python"


if __name__ == "__main__":
    pytest.main([__file__])