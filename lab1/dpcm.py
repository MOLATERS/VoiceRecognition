import numpy as np
import os
import pickle
import math
import wave

def quantize_bit(signal,alpha,bit):
    b = pow(2,bit)
    if signal > (b-1) * alpha:
        signal = b-1
    elif signal < -(b) * alpha:
        signal = -b
    else:
        signal = max(-b, min(b-1,np.floor(signal/alpha)))
    return signal + pow(2,bit)

def reverse_quantize_bit(signal,alpha,bit):
    signal -= pow(2,bit)
    return signal * alpha

def quantize_log(signal, a, min_val):
    signal -= (min_val-1)
    try:
        return math.log(signal,a)
    except:
        print(f"error at {signal}, {a}, {min_val}")
        quit()

def reverse_log(signal, a, min_val):
    return np.power(a,signal) + min_val-1

def dpcm_encode(signal,a, bit, mod):
    prediction = 0  # 初始预测值为0
    encoded_signal = []
    round = 0
    min_val = min(signal)
    for sample in signal:
        if round == 0:
            encoded_signal.append(sample)
            round += 1
            prediction = sample
            continue

        if mod == 1:
            diff = quantize_bit(sample - prediction, a, bit)  # 计算样本与预测值的差异
        if mod == 2:
            diff = quantize_log(sample - prediction, a, min_val)

        encoded_signal.append(diff)  # 将差异作为编码后的值
        
        if mod == 1:
            prediction += reverse_quantize_bit(diff,a,bit)  # 更新预测值
        if mod == 2:
            prediction += reverse_log(diff,a,min_val)  # 更新预测值


    return np.array(encoded_signal), min_val

def dpcm_decode(encoded_signal,a,bit, min_val, mod):
    prediction = 0  # 初始预测值为0
    decoded_signal = []
    round = 0
    for diff in encoded_signal:

        if round == 0:
            sample = prediction = diff
            decoded_signal.append(sample)
            round += 1
            continue

        if mod == 1:
            sample = prediction + reverse_quantize_bit(diff,a,bit)  # 重构样本值
        if mod == 2:
            sample = prediction + reverse_log(diff,a, min_val)  # 重构样本值

        decoded_signal.append(sample)
        prediction = sample  # 更新预测值
    return np.array(decoded_signal)

def calculate_SNR(original_data, decompressed_data):
    original_variance = np.var(original_data)
    k = np.mean(np.array(original_data) - np.array(decompressed_data))
    rmse = np.sqrt(np.mean(k ** 2))
    snr = 10 * np.log10(original_variance / (rmse ** 2))
    return snr

def calculate_snr(original_signal, decoded_signal):
    signal_power = np.sum(original_signal ** 2)
    diff = np.array(original_signal) - np.array(decoded_signal)
    noise_power = np.sum(diff ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def save_compressed_data(compressed_data, filename):
    # 将压缩数据转换为4位的位数组
    compressed_bits = np.packbits(np.array(compressed_data, dtype=np.int8))
    compressed_bits = np.unpackbits(compressed_bits)[:len(compressed_data)*4]
    # 将位数组保存到文件
    with open(filename, 'wb') as file:
        file.write(compressed_bits.tobytes())
    print("压缩文件保存成功：", filename, os.path.getsize(filename)/1024)

if __name__ == "__main__":
    for i in range (1,11):
        filename =f"voice/{i}.wav"
        with wave.open(filename, 'rb') as f:
            flen = f.getnframes()
            f.setpos(44)
            signal = np.frombuffer(f.readframes(flen - 44), dtype=np.int16)
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
                output_filename = f"{name}/{name}_{i}.dpc"
                save_compressed_data(encoded_signal,output_filename)





        