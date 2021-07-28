def has_PyQt5():
    """
    Check if User can import PyQt5
    
    :return: True if user can use PyQt5. Else False.
    """
    try:
        import PyQt5
        return True
    except ImportError:
        return False  
	
has_PyQt5()
