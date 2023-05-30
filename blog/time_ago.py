def time_ago(now, date):
    
    time_diff = now - date
    if time_diff.days > 365:
        time_diff = date.strftime("%d %B, %Y")
        return f'{time_diff}'
    elif time_diff.days > 7:
        time_diff = date.strftime('%B, %d')
        return f'{time_diff}'
    elif time_diff.days > 0 and time_diff.days < 7:
        time_diff = date.strftime('%A at %H:%M %p')
        return f'{time_diff}'
    elif time_diff.seconds > 3600:
        time_diff = time_diff.seconds // 3600
        return f'{time_diff} hours ago' if time_diff > 1 else f'{time_diff} hour ago'
    elif time_diff.seconds > 60:
        time_diff = time_diff.seconds // 60
        return f'{time_diff} minutes ago' if time_diff > 1 else f'{time_diff} minute ago'
    else:
        time_diff = time_diff.seconds
        return f'{time_diff} seconds ago' if time_diff > 1 else f'recently'
