#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus Overkill Obfuscation Utilities for Python
Based on the C# Overkill obfuscation from Pegasus HVNC
"""

import os
import random
import string
import shutil
from typing import List, Dict, Any

class Randomizer:
    """Generate random strings and numbers for renaming"""
    
    # Character set for generating random names
    CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    
    @staticmethod
    def next(max_value: int, min_value: int = 0) -> int:
        """Generate a random integer between min_value and max_value"""
        if min_value >= max_value:
            raise ValueError("min_value must be less than max_value")
        return random.randint(min_value, max_value - 1)
    
    @staticmethod
    def generate_random_string(size: int) -> str:
        """Generate a random string of specified size"""
        return ''.join(random.choice(Randomizer.CHARS) for _ in range(size))


class DefAnalyzer:
    """Base class for analyzing definitions"""
    
    def execute(self, context: Any) -> bool:
        """Execute the analyzer on the given context"""
        raise NotImplementedError("Subclasses must implement execute method")


class MethodDefAnalyzer(DefAnalyzer):
    """Analyzer for method definitions"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Determine if a method should be renamed"""
        # Don't rename special runtime methods
        if context.get('is_runtime_special_name', False):
            return False
            
        # Don't rename constructors
        if context.get('is_constructor', False) or context.get('is_static_constructor', False):
            return False
            
        return True


class FieldDefAnalyzer(DefAnalyzer):
    """Analyzer for field definitions"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Determine if a field should be renamed"""
        # Don't rename special runtime fields
        if context.get('is_runtime_special_name', False):
            return False
            
        # Don't rename enum constants
        if context.get('is_literal', False) and context.get('is_enum', False):
            return False
            
        return True


class PropertyDefAnalyzer(DefAnalyzer):
    """Analyzer for property definitions"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Determine if a property should be renamed"""
        # Don't rename special runtime properties
        if context.get('is_runtime_special_name', False):
            return False
            
        return True


class EventDefAnalyzer(DefAnalyzer):
    """Analyzer for event definitions"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Determine if an event should be renamed"""
        # Don't rename special runtime events
        if context.get('is_runtime_special_name', False):
            return False
            
        return True


class MemberRenamer:
    """Main class for renaming assembly members"""
    
    @staticmethod
    def string_length() -> int:
        """Get the length for generated strings"""
        return Randomizer.next(70, 50)
    
    @staticmethod
    def rename_member(member: Dict[str, Any]) -> Dict[str, Any]:
        """Rename a member with a random name"""
        member['name'] = Randomizer.generate_random_string(MemberRenamer.string_length())
        return member
    
    @staticmethod
    def rename_python_code(code: str) -> str:
        """
        Simple obfuscation for Python code - this is a placeholder implementation
        In a real implementation, this would be much more complex
        """
        # This is a very basic example - a real implementation would be much more sophisticated
        lines = code.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            # Simple example: add junk comments
            if line.strip() and not line.strip().startswith('#'):
                obfuscated_lines.append(f"# Obfuscated: {Randomizer.generate_random_string(20)}")
            obfuscated_lines.append(line)
            
        return '\n'.join(obfuscated_lines)
    
    @staticmethod
    def rename_python_file(file_path: str, output_path: str = None):
        """
        Obfuscate a Python file
        """
        if output_path is None:
            output_path = file_path
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        obfuscated_code = MemberRenamer.rename_python_code(code)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)


def obfuscate_payload(input_file: str, output_file: str) -> bool:
    """
    Obfuscate a payload file
    
    Args:
        input_file: Path to the input payload file
        output_file: Path where the obfuscated payload should be saved
        
    Returns:
        True if obfuscation was successful, False otherwise
    """
    try:
        # Copy the input file to the output location
        shutil.copy2(input_file, output_file)
        
        # If it's a Python file, apply Python-specific obfuscation
        if input_file.endswith('.py'):
            MemberRenamer.rename_python_file(output_file)
        
        return True
    except Exception as e:
        print(f"Error during obfuscation: {e}")
        return False


def main():
    """Main function for testing the obfuscation utilities"""
    print("Pegasus Overkill Obfuscation Utilities")
    print("======================================")
    
    # Example usage
    test_string = Randomizer.generate_random_string(20)
    print(f"Generated random string: {test_string}")
    
    # Test method analyzer
    method_context = {
        'is_runtime_special_name': False,
        'is_constructor': False,
        'is_static_constructor': False
    }
    
    method_analyzer = MethodDefAnalyzer()
    should_rename = method_analyzer.execute(method_context)
    print(f"Should rename method: {should_rename}")


if __name__ == "__main__":
    main()