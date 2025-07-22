import random, time

def get_current_wait_time(hospital):
    ## dummy function to get waiting time

    if hospital not in ['A', 'B', 'C', 'D', 'E']:
        return f"Hospital {hospital} not found in directory"
    
    # Simulate API call delay
    time.sleep(1)

    return random.randint(10, 10000)