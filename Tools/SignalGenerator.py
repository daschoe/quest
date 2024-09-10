"""A script to generate different stimuli patterns to use with the NeXus Trigger Interface line-in detector."""

import getopt
import sys
import soundfile as sf
import numpy as np


def write_audio_with_pattern(filepath, pattern, break_duration, subtype, amplitude, sine_duration, f, channels, fs=44100):
    """Write a sine pattern to use with the NTI."""
    # Set values to NeXus Trigger Interface bounds, if necessary
    if f < 100:
        f = 100
    elif f > 20000:
        f = 20000
    if break_duration < 10:
        break_duration = 10
    filename = ''.join(str(bit) for bit in pattern) + f'_{f}Hz_{sine_duration}ms_sine_{break_duration}ms_break.wav'

    sine = (amplitude * np.sin(2 * np.pi * np.arange(fs * (sine_duration / 1000)) * f / fs)).astype(np.float32)
    silent_break = 0 * np.arange(fs * (break_duration / 1000))
    silent_sine = 0 * np.arange(fs * (sine_duration / 1000))

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

    sf.write(f'{filepath}{filename}', final_signal, fs, subtype=subtype)


if __name__ == '__main__':
    PATTERN = [0]
    DESTINATION = "./"
    FREQUENCY = 440
    SINE_DURATION = 50
    BREAK_DURATION = 50
    AMPLITUDE = 0.5
    CHANNELS = 1
    SUBTYPE = "PCM_16"
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
            PATTERN = list(arg)
            for _, p in enumerate(PATTERN):
                p = int(p)
            print(PATTERN, type(PATTERN[0]))
        elif opt in ("-d", "--destination"):
            DESTINATION = arg
        elif opt in ("-f", "--frequency"):
            FREQUENCY = arg
        elif opt in ("-s", "--sine_duration"):
            SINE_DURATION = arg
        elif opt in ("-b", "--break_duration"):
            BREAK_DURATION = arg
        elif opt in ("-a", "--amplitude"):
            AMPLITUDE = arg
        elif opt in ("-c", "--channels"):
            CHANNELS = arg
    write_audio_with_pattern(DESTINATION, PATTERN, break_duration=BREAK_DURATION, amplitude=AMPLITUDE, sine_duration=SINE_DURATION, f=FREQUENCY, channels=CHANNELS, subtype=SUBTYPE)
