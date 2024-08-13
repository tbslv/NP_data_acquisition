*# Repo for Neuropixel Data Acquisition during sensory stimulation (Temperature, Touch).

Neural recordings were performed using Neuropixel probes (Neuropixel 1.0, IMEC) with 383 active channels. The channels closest to the tip were selected for recordings, spanning 3.84 mm of tissue. Data streams were sent to the IMEC PXIe-1000 Base Station, which was housed in a National Instruments PXIe-1071 chassis and connected to a PCIe-8371 card in the acquisition computer via the National Instruments PXIe-8370 module. Data streams were saved as continuous data files.

Grounding & Reference:
The last grounding pad located on the arm of the Neuropixel Flex Cable arm was soldered to a silver wire that was in electrical contact with the main ground of the experimental setup.
A silver wire coated with chloride served as the reference electrode during extracellular recordings when in contact with Ringer’s solution. The backside of that silver wire was connected to the Neuropixel probe reference pad.

Data Acquisition:
Neuropixel data acquisition was done with 30 kHz sampling rate and 500 x gain for the spike band and with 2.5 kHz sampling rate and 250 x gain for the LFP band. Open Ephys GUI (https://open-ephys.org/gui ) was used as acquisition software. Each probe was connected to the Imec HS-1000 head stage, and data was sent to the Imec PXIe-1000 Base Station via the Imec CBL-1000 cable. The base station was housed in a National Instruments PXIe-1071 chassis, which was connected to a National Instruments PCIe-8371 card inside the data acquisition computer via the National Instruments PXIe-8370 module.

Synchronization:
Synchronization of simultaneously recorded spike bands and stimulus application was achieved by sending TTL pulses to the Imec PXIe-1000 Base Station at the beginning of each trial and at the timepoint of sensory stimulation, which were registered by both probes led to the synchronization of both data streams. The same TTL pulse was also used to trigger the QST-Lab TCS box, which led to the synchronization of the neural data with the stimulus application. To compensate for the individual sampling rates of Neuropixel probes, the neural data was aligned to each TTL encoding the trial start.

Stimulus Application:
Temperature was applied via a gold-plated Peltier element, which was part of the QST-Lab probe head (https://www.qst-lab.eu/probes?lightbox=dataItem-jxob7q0t__item-kikehpv8 ) The probe head was connected to the QST-Lab TCS control box (https://www.qst-lab.eu/tcs-technical-description ), which in turn was connected to the National Instruments BNC-2090A breakout box. The breakout box was connected to a National Instruments PCIe-6323 card inside the stimulus computer. This signal chain served to apply stimuli, which were triggered by a custom Python script (TempStim_Recording.py) running on the stimulus computer throughout the experiments, as well as to record the feedback temperature of the Peltier elements, as measured by thermocouples placed on top of the Peltier elements. The feedback temperature was recorded in a trial-by-trial manner, and the data was stored for further analysis.

