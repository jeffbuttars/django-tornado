"""
Enable auditing of decorators, what decorators run and HttpClient ops.

Allow for realtime and delayed group commits. 
Realtime being every audit message is commited as it's created. 
Delayed/grouped allowing multiple audit messages to be commited at once after
a given period of time.

Initially support DB audit trail and log file based audit trail.
"""
