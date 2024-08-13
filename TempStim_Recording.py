import numpy as np
import pandas as pd
import datetime
import os
import pickle
import nidaqmx
import time
import serial

from Initialize_Recording import InitializeRec
#from input_functions_np import merge_AI_files_temp
from nidaqmx.constants import WAIT_INFINITELY

class TempStimRec:
    def __init__(self, samplingrate=1000, port='COM3', baudrate=115200, 
                    bytesize=serial.EIGHTBITS, timeout=10,sweeplength=None, 
                    baseline_temp=None, stimulus_temp=None, stim_time_pre=None, 
                    stim_duration_tot=None,n_repetitions=None, on_ramp=None, baseline_time=None
                    off_ramp=None, freq=None, active_zones='11110', 
                    working_directory=None, exp_ID=None):

        self.samplingrate = samplingrate
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.ser = self.init_serial()

        self.sweeplength = sweeplength
        self.baseline_temp = baseline_temp
        self.stimulus_temp = stimulus_temp
        self.stim_time_pre = stim_time_pre
        self.stim_duration_tot = stim_duration_tot
        self.n_repetitions = n_repetitions
        self.on_ramp = on_ramp
        self.off_ramp = off_ramp
        self.freq = freq
        self.active_zones = active_zones
        self.baseline_time = baseline_time

        self.working_directory = working_directory
        self.exp_ID = exp_ID

    def init_serial(self):
        """Initializes the serial communication."""
        ser = serial.Serial(
            port=self.port,
                            baudrate=self.baudrate,
                            bytesize=self.bytesize, 
                            timeout=self.timeout
                            )
        return ser

    def build_command(self):
        """Builds a command string for temperature control."""
        if self.on_ramp >= 1000:
            string = 'S{} N{} C0{} D0{}00 V0{} R0{}'.format(
                                            self.active_zones,
                                            int(10 * self.baseline_temp), 
                                            int(10 * self.stimulus_temp),
                                            int(10 * self.stim_duration_tot),
                                            int(10 * self.on_ramp),
                                            int(10 * self.off_ramp))
        else:
            string = 'S{} N{} C0{} D0{}00 V00{} R00{}'.format(
                                            self.active_zones,
                                            int(10 * self.baseline_temp),
                                            int(10 * self.stimulus_temp),
                                            int(10 * self.stim_duration_tot),
                                            int(10 * self.on_ramp),
                                            int(10 * self.off_ramp))
        print(string)
        return string

    def get_combination_temp(self):
        """Generates randomized combinations of baseline and stimulus temperatures."""
        [baseline_temp_all, stimulus_temp_all] = np.meshgrid(
                                                        self.baseline_temp,
                                                        self.stimulus_temp)
        baseline_temp_all = baseline_temp_all.flatten()
        stimulus_temp_all = stimulus_temp_all.flatten()
        n_trials = int(self.n_repetitions * len(baseline_temp_all))

        all_trials_base = []
        all_trials_stim = []

        for n in range(self.n_repetitions):
            sequence = np.random.permutation(len(baseline_temp_all))
            baseline_temp_all_tmp = [baseline_temp_all[s] for s in sequence]
            stimulus_temp_all_tmp = [stimulus_temp_all[s] for s in sequence]

            all_trials_base = np.concatenate((all_trials_base, baseline_temp_all_tmp), axis=0)
            all_trials_stim = np.concatenate((all_trials_stim, stimulus_temp_all_tmp), axis=0)

        combinationen = np.unique(all_trials_stim)
        ids = np.zeros(len(all_trials_stim))

        for i in range(len(combinationen)):
            ids[np.where(all_trials_stim == float(combinationen[i]))] = i


        self.trials = n_trials
        self.all_trials_base_temp = all_trials_base
        self.all_trials_stim_temp = all_trials_stim
        self.ids = ids

        return 

    def build_sweep_TTL(self):
        """Builds a TTL sweep signal."""
        datapoints_pre = np.arange(0, self.stim_time_pre * self.samplingrate)
        datapoints_stim_tot = np.arange(0, self.stim_duration_tot * self.samplingrate)

        sweep_output = np.zeros([3, self.sweeplength * self.samplingrate], dtype=np.bool)

        start_stimulus_index = len(datapoints_pre)
        end_stimulus_index = start_stimulus_index + len(datapoints_stim_tot)

        sweep_output[0, :1 * self.samplingrate] = True
        sweep_output[1, start_stimulus_index:end_stimulus_index] = True
        sweep_output[2, start_stimulus_index:end_stimulus_index] = True

        return sweep_output

    def build_sweep_temp(self):
        """Builds a temperature sweep signal."""
        sweep_output = np.zeros([2, self.sweeplength * self.samplingrate])

        stepsize = self.samplingrate / self.freq
        duty = stepsize / 2
        ups = np.arange(0, (self.sweeplength * self.samplingrate),
        stepsize).astype(int)
        downs = np.arange(duty, self.sweeplength * self.samplingrate, stepsize).astype(int)

        size = downs[0] - ups[0]
        print(size)

        sweep_output[1, ups[0]:ups[-1]] = 5

        for i in range(ups.size):
            sweep_output[0, ups[i]:downs[i]] = 5

        return sweep_output

    def save_file_temp(self):
        """Saves temperature sweep parameters to a file."""
        save_file = {
            'Trials': self.trials,
            'Baseline Temp': self.all_trials_base_temp,
            'Stimulus Temp': self.all_trials_stim_temp,
            'Samplingrate': self.samplingrate,
            'Sweeplength': self.sweeplength,
            'Pre Stimulus Time': self.stim_time_pre,
            'Stimulus Duration': self.stim_duration_tot,
            'Repititions': self.n_repetitions,
            'ID': self.exp_ID,
            'sweepID': self.ids,
            'OnRamp': self.on_ramp,
            'OffRamp': self.off_ramp,
            'PupilFreq': self.freq,
            'active_zones': self.active_zones
        }

        save_file_DF = pd.DataFrame.from_dict(save_file, orient='columns')
        name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = self.exp_ID + '_' + name + '_sweepParameter'
        save_file_DF.name = name
        path = os.path.join(self.working_directory, name)

        save_file_DF.to_pickle(path)
        return path

    def merge_AI_files_temp (self):
        """Merge multiple AI files (FeedbackTemp, Pawmovement...)."""

        listdir = []
        for i in os.listdir(self.wd):
            if self.exp_ID + '_' in i and '_input' in i:
                listdir.append(i)
        for z in range(len(listdir)):
            data_temp = np.load(os.path.join(self.wd,listdir[z]))
            if z == 0:
                data_tot = data_temp
                #os.remove(os.path.join(wd,listdir[z]))
            else:
                data_tot = np.dstack((data_tot,data_temp))
                #os.remove(os.path.join(wd,listdir[z]))
        try:        
            os.makedirs(os.path.join(self.wd,'AI_files_'+self.exp_ID))
        except:
            pass

        np.save(os.path.join(wd,'AI_files_'+exp_ID,'temp_AI'), data_tot)

        return

    @staticmethod
    def save_obj(obj, working_directory, name):
        """Saves an object to a pickle file."""
        with open(working_directory + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_obj(working_directory, name):
        """Loads an object from a pickle file."""
        with open(working_directory + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def send_command(ser, string):
        """Sends a command string via serial communication."""
        for i in string:
            command = bytearray(i, ('utf-8'))
            ser.write(command)
            time.sleep(0.002)
        return

    def run_temp_task(self):
        """Performs the temperature task."""


        # Update instance variables based on input arguments

        trials, all_trials_base, all_trials_stim, combinationen, ids = self.get_combination_temp()

        self.save_file_temp(trials, all_trials_base, all_trials_stim, ids)

        write_task, read_task, sample_clk_task, write_task_dig1, writer, reader = InitializeRec(
            self.samplingrate, range(self.samplingrate * self.sweeplength))

        baseline_time = 60 * self.baseline_time
        time.sleep(baseline_time)

        for t in range(trials):
            start = time.time()
            print('Trial number: {} of {} trials'.format(t + 1, trials))
            data = np.zeros([7, self.sweeplength * self.samplingrate], dtype=np.float64)

            base_temp = all_trials_base[t]
            stim_temp = all_trials_stim[t]

            sweep_output = self.build_sweep_temp()
            ttl_sweep = self.build_sweep_TTL()

            command = self.build_command()
            self.send_command(self.ser, command)

            writer.write_many_sample(sweep_output)
            write_task_dig1.write(ttl_sweep, auto_start=False)

            act_trialstart = time.time()
            print('Preparation took {:3.3f} secs'.format(act_trialstart - start))

            write_task.start()
            read_task.start()
            write_task_dig1.start()
            sample_clk_task.start()

            reader.read_many_sample(data, number_of_samples_per_channel=self.sweeplength * self.samplingrate, timeout=WAIT_INFINITELY)
            sample_clk_task.wait_until_done(timeout=self.sweeplength + 2)

            write_task.stop()
            read_task.stop()
            write_task_dig1.stop()
            sample_clk_task.stop()

            np.save(os.path.join(self.working_directory, self.exp_ID + '_{0:03d}_input'.format(t)), data)

            end = time.time()

            print('Trial took {:3.3f} secs'.format(end - start))

        sample_clk_task.close()
        write_task.close()
        read_task.close()
        write_task_dig1.close()

        merge_AI_files_temp(self.working_directory, self.exp_ID)

        return trials, all_trials_base, all_trials_stim, combinationen, ids
