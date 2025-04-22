from datetime import datetime

time_string1 = '오전 9:46'.replace('오전','AM').replace('오후','PM')
time_string2 = '오후 9:46'.replace('오전','AM').replace('오후','PM')

# Specify the format of the time string
time_format = '%p %I:%M'

# Parse the time string
parsed_time = datetime.strptime(time_string1, time_format)
# Access the parsed time components
hour = parsed_time.hour
minute = parsed_time.minute

print(hour, minute, parsed_time)


# Parse the time string
parsed_time = datetime.strptime(time_string2, time_format)
# Access the parsed time components
hour = parsed_time.hour
minute = parsed_time.minute

print(hour, minute, parsed_time)
