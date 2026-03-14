"""
JSON I/O module for Business Financing Readiness Tool
Handles saving and loading project data
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple


def create_project_data(
    project_name: str,
    project_notes: str,
    inputs: Dict,
    results: Dict
) -> Dict:
    """
    Create a project data structure for saving
    
    Args:
        project_name: Name of the project
        project_notes: Project notes
        inputs: Dictionary of all input values
        results: Dictionary of calculated results
        
    Returns:
        Complete project data dictionary
    """
    return {
        'project_name': project_name,
        'created_date': datetime.now().isoformat(),
        'project_notes': project_notes,
        'inputs': inputs,
        'results': results
    }


def save_project(
    project_data: Dict,
    filename: Optional[str] = None,
    directory: str = "saved_projects"
) -> Tuple[bool, str]:
    """
    Save project data to JSON file
    
    Args:
        project_data: Project data dictionary
        filename: Optional filename (will be auto-generated if not provided)
        directory: Directory to save file in
        
    Returns:
        Tuple of (success, filepath or error message)
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name_clean = project_data.get('project_name', 'project').replace(' ', '_')
            filename = f"financing_analysis_{project_name_clean}_{date_str}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(directory, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        return True, filepath
    
    except Exception as e:
        return False, f"Error saving project: {str(e)}"


def load_project(filepath: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Load project data from JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Tuple of (success, project_data or None, message)
    """
    try:
        if not os.path.exists(filepath):
            return False, None, f"File not found: {filepath}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Validate required fields
        required_fields = ['project_name', 'created_date', 'inputs']
        missing_fields = [field for field in required_fields if field not in project_data]
        
        if missing_fields:
            return False, None, f"Invalid project file. Missing fields: {', '.join(missing_fields)}"
        
        return True, project_data, "Project loaded successfully"
    
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON file: {str(e)}"
    except Exception as e:
        return False, None, f"Error loading project: {str(e)}"


def list_saved_projects(directory: str = "saved_projects") -> list:
    """
    List all saved project files in directory
    
    Args:
        directory: Directory to search for project files
        
    Returns:
        List of tuples (filename, filepath, modified_time)
    """
    if not os.path.exists(directory):
        return []
    
    projects = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            modified_time = os.path.getmtime(filepath)
            projects.append((filename, filepath, modified_time))
    
    # Sort by modified time (newest first)
    projects.sort(key=lambda x: x[2], reverse=True)
    
    return projects


def export_to_json_string(project_data: Dict) -> str:
    """
    Export project data to JSON string for download
    
    Args:
        project_data: Project data dictionary
        
    Returns:
        JSON string
    """
    return json.dumps(project_data, indent=2, ensure_ascii=False)


def import_from_json_string(json_string: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Import project data from JSON string
    
    Args:
        json_string: JSON string containing project data
        
    Returns:
        Tuple of (success, project_data or None, message)
    """
    try:
        project_data = json.loads(json_string)
        
        # Validate required fields
        required_fields = ['project_name', 'inputs']
        missing_fields = [field for field in required_fields if field not in project_data]
        
        if missing_fields:
            return False, None, f"Invalid project data. Missing fields: {', '.join(missing_fields)}"
        
        return True, project_data, "Project imported successfully"
    
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, None, f"Error importing project: {str(e)}"
