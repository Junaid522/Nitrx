from datetime import datetime


def convert_time(created_at):
    time = (datetime.today()).replace(tzinfo=None) - (created_at).replace(tzinfo=None)
    if time.days:
        if time.days > 365:
            return f'{int(time.days / 365)} years ago'
        elif time.days > 30:
            return f'{int(time.days / 30)} months ago'
        elif time.days > 7:
            return f'{int(time.days / 7)} months ago'
        return f'{time.days} days ago'
    else:
        new_time = time.seconds % (24 * 3600)
        hour = new_time // 3600
        if hour:
            return f'{int(hour)} hours ago'
        new_time %= 3600
        minutes = new_time // 60
        if minutes:
            return f'{int(minutes)} minutes ago'
        elif time.seconds:
            return f'{int(time.seconds)} seconds ago'


def convert_time_mhr(created_at):
    time = (datetime.today()).replace(tzinfo=None) - (created_at).replace(tzinfo=None)
    if time.days:
        if time.days > 365:
            return f'{int(time.days / 365)} years ago'
        elif time.days > 30:
            return f'{int(time.days / 30)} months ago'
        elif time.days > 7:
            return f'{int(time.days / 7)} months ago'
        return f'{time.days} days ago'
    else:
        new_time = time.seconds % (24 * 3600)
        hour = new_time // 3600
        if hour:
            return f'{int(hour)}hr ago'
        new_time %= 3600
        minutes = new_time // 60
        if minutes:
            return f'{int(minutes)}m ago'
        elif time.seconds:
            return f'{int(time.seconds)}s ago'
