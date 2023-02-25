from settings import DANGER_LENGTH_HOURS
import math

print("Hours: ", DANGER_LENGTH_HOURS)

left_time_seconds = DANGER_LENGTH_HOURS*60*60 - (1600 - 6)

print(left_time_seconds)


hours_decimal = left_time_seconds/60.0/60.0

hours = math.floor(hours_decimal)

mins_decimal = (hours_decimal-hours)*60.0

mins = math.floor(mins_decimal)

secs = (mins_decimal - mins)*60.0




print("left hours: ", hours)
print("left mins: ", mins)

print("left secs: ", secs)
