from keeper import app

@app.template_filter('formatdatetime')
def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter('format_float_string')
def format_float_string(value):
    """Format a string float"""
    if value is None:
        return ""
    angle = float(value)
    return "{:6.2f}".format(angle)

@app.template_filter('format_int')
def format_int(value):
    """Format a int with commas"""
    if value is None:
        return ""

    return "{:,.0f}".format(int(value))
