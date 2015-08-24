def get_next_pred_occupied_slot(timestamp):
    """
    Provides the minutes to the next occupied slot
    """
    # choose the file that describes the occupancy prediction pattern
    with open('sim_data/pred_occupancy_scen2') as f:
        occ_data = f.readlines()

    current_slot = timestamp.hour * 4 + timestamp.minute / 15
    next_occupied_slot = int(current_slot)
    while int(occ_data[next_occupied_slot].strip()) == 0:
        next_occupied_slot = (next_occupied_slot + 1) % 96
    if next_occupied_slot >= current_slot:
        free_time = (next_occupied_slot - current_slot) * 15
    else:
        free_time = (96 - current_slot + next_occupied_slot) * 15
    return free_time


def is_occupied(timestamp):
    """
    returns whether or not the building is occupied at timeslot
    """
    # return 1
    current_slot = timestamp.hour * 4 + timestamp.minute / 15
    # choose the file that describes the occupancy sim pattern
    with open('sim_data/sim_occupancy_scen2') as f:
        occ_data = f.readlines()
    return int(occ_data[int(current_slot)].strip()) == 1
