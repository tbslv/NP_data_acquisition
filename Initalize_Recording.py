import nidaqmx
import nidaqmx.system

from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx.constants import AcquisitionType, Edge, TerminalConfiguration, LineGrouping
from nidaqmx.utils import flatten_channel_string

import numpy as np

class InitializeRec:
    def __init__(self, samplingrate, dp_sweeplength, devname='Dev1'):
        """
        Initializes and configures the NI DAQ session.
        
        Parameters:
        - samplingrate: The sampling rate for the acquisition.
        - dp_sweeplength: The sweep length (number of samples).
        - devname: The name of the device to use (default is 'Dev1').
        """
        self.samplingrate = samplingrate
        self.dp_sweeplength = dp_sweeplength
        self.devname = devname
        self.system = self.list_available_devices()
        self.validate_device_name()

        self.write_task = nidaqmx.Task()
        self.read_task = nidaqmx.Task()
        self.sample_clk_task = nidaqmx.Task()
        self.write_task_dig1 = nidaqmx.Task()

        self.samp_clk_terminal = self.configure_sample_clock()

        self.writer = None
        self.reader = None

        self.sample_clk_line=0

        self.do_lines = ["port0/line0:4"]
        self.line_grouping = LineGrouping.CHAN_PER_LINE

        self.ao_channels = [0, 1, 2]
        self.ao_names = ["Eyetracking", "Forepawtouch", "Opto"]
        self.ao_max_vals = [10, 1, 10]
        self.ao_min_vals = [-10, -1, -10]

        self.ai_channels = [1, 2, 3, 4, 5, 6, 7]
        self.ai_max_vals = [2.5, 10, 10, 10, 10, 10, 10]
        self.ai_min_vals = [0, -10, -10, -10, -10, -10, -10]
        self.terminal_configs = [TerminalConfiguration.RSE] * len(self.ai_channels)


        self.configure_tasks()

    def list_available_devices(self):
        """Lists all available DAQ devices connected to the local system."""
        system = nidaqmx.system.System.local()
        for device in system.devices:
            print(f'Device Name: {device.name}, Product Category: {device.product_category}, Product Type: {device.product_type}')
        print('')
        return system

    def validate_device_name(self):
        """Validates if the provided device name exists in the system."""
        if self.devname not in [device.name for device in self.system.devices]:
            raise ValueError(f"Device '{self.devname}' not found. Please check the device name and try again.")

    def configure_sample_clock(self):
    """
    Configures the sample clock task with a given frequency and sample length.

    Args:
        line: The counter line number to use (default is 0).
   
    """
    self.sample_clk_task.co_channels.add_co_pulse_chan_freq(f'{self.devname}/ctr{self.sample_clk_line}', freq=self.samplingrate)
    self.sample_clk_task.timing.cfg_implicit_timing(
        sample_mode=AcquisitionType.FINITE, samps_per_chan=len(self.dp_sweeplength))
    terminal_path = f'/{self.devname}/Ctr{line}InternalOutput'
    print(terminal_path)
    return terminal_path


    def configure_digital_output_channels(self):
        """Configures digital output channels."""
        

        for line in self.do_lines:
            self.write_task_dig1.do_channels.add_do_chan(
                flatten_channel_string([f"{self.devname}/{line}"]),
                line_grouping=self.line_grouping
            )

        self.write_task_dig1.timing.cfg_samp_clk_timing(
            rate=self.samplingrate,
            source=self.samp_clk_terminal,
            active_edge=Edge.RISING,
            sample_mode=AcquisitionType.FINITE,
            samps_per_chan=len(self.dp_sweeplength)
        )

    def configure_analog_output_channels(self):
        """Configures analog output channels."""
    

        for i, channel in enumerate(self.ao_channels):
            self.write_task.ao_channels.add_ao_voltage_chan(
                flatten_channel_string([f"{self.devname}/ao{self.channel}"]),
                max_val=self.ao_max_vals[i],
                min_val=self.ao_min_vals[i],
                name_to_assign_to_channel=self.ao_names[i]
            )

        self.write_task.timing.cfg_samp_clk_timing(
            rate=self.samplingrate,
            source=self.samp_clk_terminal,
            active_edge=Edge.RISING,
            sample_mode=AcquisitionType.FINITE,
            samps_per_chan=len(self.dp_sweeplength)
        )

        self.writer = AnalogMultiChannelWriter(self.write_task.out_stream, auto_start=False)

    def configure_analog_input_channels(self):
        """Configures analog input channels."""

        for i, channel in enumerate(self.ai_channels):
            self.read_task.ai_channels.add_ai_voltage_chan(
                flatten_channel_string([f"{self.devname}/ai{self.channel}"]),
                max_val=self.ai_max_vals[i],
                min_val=self.ai_min_vals[i],
                terminal_config=self.terminal_configs[i]
            )

        self.read_task.timing.cfg_samp_clk_timing(
            rate=self.samplingrate,
            source=self.samp_clk_terminal,
            active_edge=Edge.RISING,
            sample_mode=AcquisitionType.CONTINUOUS
        )

        self.reader = AnalogMultiChannelReader(self.read_task.in_stream)

    def configure_tasks(self):
        """Configures all tasks: analog output, analog input, and digital output."""
        self.configure_analog_output_channels()
        self.configure_analog_input_channels()
        self.configure_digital_output_channels()

    def get_tasks(self):
        """Returns the configured tasks."""
        return self.write_task, self.writer, self.read_task, self.sample_clk_task, self.write_task_dig1
