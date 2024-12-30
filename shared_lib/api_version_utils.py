"""API version validation utilities."""

import json
from pathlib import Path
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class APIVersionError(Exception):
    """Raised when API version is incompatible."""
    pass

class APIFeatureError(Exception):
    """Raised when required API feature is not available."""
    pass

def load_api_versions() -> Dict[str, Any]:
    """Load API version information from config."""
    version_file = Path(__file__).parent.parent / 'config' / 'api_versions.json'
    with open(version_file) as f:
        return json.load(f)

def verify_api_compatibility(api_name: str, service: Any) -> Optional[str]:
    """Verify API compatibility.
    
    Args:
        api_name: Name of API to verify
        service: API service object
        
    Returns:
        Optional[str]: Error message if incompatible, None if compatible
        
    Raises:
        APIVersionError: If API version is incompatible
        APIFeatureError: If required features are not available
    """
    versions = load_api_versions()
    if api_name not in versions:
        raise ValueError(f"Unknown API: {api_name}")
        
    api_info = versions[api_name]
    
    # Check version lifecycle
    if api_info.get('deprecation_date'):
        deprecation_date = datetime.strptime(
            api_info['deprecation_date'], 
            '%Y-%m-%d'
        )
        if datetime.now() > deprecation_date:
            return f"API version deprecated since {api_info['deprecation_date']}"
            
    # Check breaking changes
    breaking_changes = api_info.get('breaking_changes', [])
    if breaking_changes:
        recent_changes = [
            change for change in breaking_changes
            if (datetime.now() - datetime.strptime(change['date'], '%Y-%m-%d')
                < timedelta(days=90))
        ]
        if recent_changes:
            return f"Recent breaking changes: {recent_changes}"
            
    return None

def verify_required_features(api_name: str, service: Any) -> List[str]:
    """Verify all required features are available.
    
    Args:
        api_name: Name of API to verify
        service: API service object
        
    Returns:
        List[str]: List of missing features
    """
    versions = load_api_versions()
    api_info = versions[api_name]
    
    missing_features = []
    
    for feature in api_info.get('features_required', []):
        parts = feature.split('.')
        obj = service
        try:
            for part in parts:
                obj = getattr(obj, part)
            if not callable(obj):
                missing_features.append(feature)
        except AttributeError:
            missing_features.append(feature)
            
    return missing_features

def check_api_status(api_name: str) -> Optional[str]:
    """Check API status page for issues.
    
    Args:
        api_name: Name of API to check
        
    Returns:
        Optional[str]: Warning message if issues found
    """
    versions = load_api_versions()
    api_info = versions[api_name]
    
    status_url = api_info.get('status_url')
    if not status_url:
        return None
        
    try:
        response = requests.get(status_url, timeout=5)
        if response.status_code != 200:
            return f"API status check failed: {response.status_code}"
            
        # TODO: Implement status page parsing for specific APIs
        return None
    except requests.RequestException as e:
        return f"Failed to check API status: {str(e)}"

def verify_gmail_version(service: Any) -> Optional[str]:
    """Verify Gmail API version compatibility.
    
    Args:
        service: Gmail API service object
        
    Returns:
        Optional[str]: Error message if incompatible
    """
    # Check basic compatibility
    if error := verify_api_compatibility('gmail', service):
        return error
        
    # Check required features
    if missing := verify_required_features('gmail', service):
        return f"Missing required features: {missing}"
        
    # Check API status
    if warning := check_api_status('gmail'):
        logger.warning(f"Gmail API status: {warning}")
        
    return None

def check_api_changelog(api_name: str) -> Optional[str]:
    """Check API changelog for updates.
    
    Args:
        api_name: Name of the API to check
        
    Returns:
        Optional[str]: Warning message if changes detected, None otherwise
    """
    versions = load_api_versions()
    api_info = versions[api_name]
    
    # Skip if no changelog URL
    if not api_info.get('changelog_url'):
        return None
        
    try:
        response = requests.get(api_info['changelog_url'], timeout=5)
        if response.status_code == 200:
            # TODO: Implement changelog parsing logic
            # For now, just check if the page has changed
            content_hash = hash(response.text)
            return f"Changelog updated for {api_name} - please review"
    except Exception:
        return f"Failed to check changelog for {api_name}"
    
    return None

def monitor_api_versions():
    """Monitor API versions for updates and issues.
    
    Returns:
        Dict[str, List[str]]: Issues found per API
    """
    versions = load_api_versions()
    issues = {}
    
    for api_name, api_info in versions.items():
        api_issues = []
        
        # Check last verification date
        last_verified = datetime.strptime(
            api_info['last_verified'], 
            '%Y-%m-%d'
        )
        days_since_verify = (datetime.now() - last_verified).days
        if days_since_verify > 30:
            api_issues.append(
                f"Not verified for {days_since_verify} days"
            )
            
        # Check changelog
        if warning := check_api_changelog(api_name):
            api_issues.append(warning)
            
        # Check status
        if warning := check_api_status(api_name):
            api_issues.append(warning)
            
        if api_issues:
            issues[api_name] = api_issues
            
    return issues

def update_last_verified(api_name: str):
    """Update the last verification date for an API."""
    version_file = Path(__file__).parent.parent / 'config' / 'api_versions.json'
    with open(version_file) as f:
        versions = json.load(f)
    
    versions[api_name]['last_verified'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(version_file, 'w') as f:
        json.dump(versions, f, indent=4)

def verify_all_apis() -> Dict[str, str]:
    """Verify all APIs and return status messages."""
    versions = load_api_versions()
    results = {}
    
    for api_name in versions:
        # Check changelog
        changelog_msg = check_api_changelog(api_name)
        if changelog_msg:
            results[api_name] = changelog_msg
            
        # Check last verification date
        last_verified = datetime.strptime(
            versions[api_name]['last_verified'], 
            '%Y-%m-%d'
        )
        days_since_verify = (datetime.now() - last_verified).days
        
        if days_since_verify > 30:
            results[api_name] = f"API not verified for {days_since_verify} days"
            
    return results
