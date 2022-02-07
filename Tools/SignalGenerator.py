"""A script to generate different stimuli patterns to use with the NeXus Trigger Interface line-in detector."""

import getopt
import sys
import soundfile as sf
import numpy as np


def write_audio_with_pattern(filepath, pattern, break_duration=10, subtype="PCM_16", amplitude=0.5, fs=44100, sine_duration=500, f=0, channels=1):
    """Write a sine pattern to use with the NTI."""
    # Set values to NeXus Trigger Interface bounds, if necessary
    if f < 100:
        f = 100
    elif f > 20000:
        f = 20000
    if break_duration < 10:
        break_duration = 10
    filename = ''.join(str(bit) for bit in pattern)+"_{}Hz_{}ms_sine_{}ms_break.wav".format(f, sine_duration, break_duration)

    sine = (amplitude * np.sin(2 * np.pi * np.arange(fs * (sine_duration/1000)) * f / fs)).astype(np.float32)
    silent_break = 0 * np.arange(fs * (break_duration/1000))
    silent_sine = 0 * np.arange(fs * (sine_duration/1000))

    final_signal = []
    final_signal.extend(silent_break)
    for bit in pattern:
        if bit == 1:
            final_signal.extend(sine)
        else:
            final_signal.extend(silent_sine)
        final_signal.extend(silent_break)
    final_signal = np.array(final_signal)

    if channels > 1:
        multichannel = np.array((len(final_signal), channels))
        for ch in range(channels):
            multichannel[:, ch] = final_signal
        final_signal = multichannel

    sf.write(filepath+filename, final_signal, fs, subtype=subtype)


if __name__ == '__main__':
    pattern = [0]
    destination = "./"
    frequency = 440
    sine_duration = 50
    break_duration = 50
    amplitude = 0.5
    channels = 1
    subtype = "PCM_16"
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hp:d:f:s:b:a:c:", ["pattern=", "destination=", "frequency=", "sine_duration=", "break_duration=", "amplitude=", "channels="])
    except getopt.GetoptError:
        print('SignalGenerator.py -p <pattern> [-d <path_to_save_destination> -f <frequency> -s <sine_duration> -b <break_duration> -a <amplitude> -c <number_of_channels>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print()
            sys.exit('SignalGenerator.py -p <pattern> [-d <path_to_save_destination> -f <frequency> -s <sine_duration> -b <break_duration> -a <amplitude> -c <number_of_channels>]')
        elif opt in ("-p", "--pattern"):
            pattern = list(arg)
            for p in range(len(pattern)):
                pattern[p] = int(pattern[p])
            print(pattern, type(pattern[0]))
        elif opt in ("-d", "--destination"):
            destination = arg
        elif opt in ("-f", "--frequency"):
            destination = arg
        elif opt in ("-s", "--sine_duration"):
            destination = arg
        elif opt in ("-b", "--break_duration"):
            destination = arg
        elif opt in ("-a", "--amplitude"):
            destination = arg
        elif opt in ("-c", "--channels"):
            destination = arg
    write_audio_with_pattern(destination, pattern, break_duration=break_duration, amplitude=amplitude, sine_duration=sine_duration, f=frequency, channels=channels)
