import pywhatkit as kit

# Phone number must include country code. Example: +91 for India
phone_number = "+919495854250"  # replace with your number
message = "Hello! This is a test from Python."
hour = 20  # 24-hour format
minute = 52 # set it 1-2 minutes ahead of current time

kit.sendwhatmsg(phone_number, message, hour, minute)
