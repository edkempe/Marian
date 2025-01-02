"""String utility functions."""

def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        snake_str: String in snake_case format
        
    Returns:
        String in camelCase format
    """
    if not snake_str:
        return snake_str
        
    # Handle already camel case
    if any(c.isupper() for c in snake_str):
        return snake_str
        
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
