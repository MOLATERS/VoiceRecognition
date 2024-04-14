import numpy as np
from func import *
import wave

if __name__ == "__main__":
    for i in range (1,11):
        filename =f"voice/{i}.wav"
        signal = read_file(filename)
        for mod in range(1,3):
            for bit in {3,7}:
                result = []
                a = 75
                if mod == 1:
                    if bit == 3:
                        name = "bit4"
                    elif bit == 7:
                        name = "bit8"
                elif mod == 2:
                    name = "log"
                encoded_signal, min_val = dpcm_encode(signal,a,bit, mod)
                decoded_signal = dpcm_decode(encoded_signal,a,bit,min_val, mod)
                snr = calculate_SNR(signal, decoded_signal)
                snr2 = calculate_snr(signal, decoded_signal)
                result.append((a,snr,snr2))
                print(snr,snr2)
                output_filename = f"{name}/encode/{name}_{i}.dpc"
                pcm_filename = f"{name}/decode/{name}_{i}.pcm"
                save_compressed_data(encoded_signal,output_filename)
                data = read_compressed_data(output_filename,len(signal))
                write_pcm_file(pcm_filename,data)






        