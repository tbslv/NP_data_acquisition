import os


working_directory = 'C:\Data\JPO-test'

if not os.path.isdir(working_directory):
    os.makedirs(working_directory)

from Initalize_Recording import InitializeRec
from TempStim_Recording import TempStimRec


# combi_TL
combi = ([32],[42,41,40,38,35,32,31,30,28,26,22],20,25,2,9,0,75,75,40)

# combi_HAB
#combi = ([32],[42,41,40,39,38,35,32,31,30,29,28,26,22],20,25,2,9,1,75,75,40)
#combi = ([32],[41,25],20,25,2,9,0,75,75,40)


# order of combination_file
# ----------------------
# baseline temp (list) 			[0]
# stimulus temp (list) 			[1]
# sweeplength [s] (int) 		[2]
# trials per stim (int) 		[3]
# stim duration [s] (int) 		[4]
# pre stim time [s] (int) 		[5]
# baseline time in [min] (int)	[6]
# on-ramp 						[7]
# off-ramp						[8]
# eyetracking frequenz 			[9]






ID = '001'

TempStimRec(sweeplength=combi[2], baseline_temp=combi[0], stimulus_temp=combi[1],
			stim_time_pre=combi[5], stim_duration_tot=combi[4],n_repetitions=combi[3],
			on_ramp=combi[7], baseline_time=combi[6],off_ramp=combi[8], freq=combi[9],
            working_directory=working_directory, exp_ID=ID)

trials,all_trials_base,all_trials_stim, combinationen, ids = run_temp_task()