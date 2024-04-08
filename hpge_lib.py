import numpy as np

def open_data(data_source):
    """
    Open a .mpa file and returns the data saved as a Python list and the information necessary to
    split by different ADCs 
    Input:
    - data_source: path of the .mpa file
    Output: 
    - datas        : Python list containing all the data read from the .mpa text file 
    - adcs_flag_pos: indexes of the cells in the "datas" list containing the first row
                     of the ADCs' headers
    - data_flag_pos: indexes of the cells in the "datas" list containing the first row
                     of the ADCs' data
    """

    with open(data_source, 'r') as data_file:
        datas = data_file.read().splitlines()

    min_adc = 1
    max_adc = 4

    adcs_flag_pos = [datas.index('[ADC{0}]'.format(i)) for i in range(min_adc,max_adc+1)]
    adcs_ranges   = [int(datas[pos + 1].split('=')[1])   for pos in adcs_flag_pos]
    data_flag_pos = [datas.index('[DATA{0},{1} ]'.format(i, adcs_ranges[i])) for i in range(max_adc)]

    data_flag_pos.append(len(datas))
    adcs_flag_pos.append(data_flag_pos[0])

    return datas, adcs_flag_pos, data_flag_pos

def read_ADC_data(datas, adc_num, adcs_flag_pos, data_flag_pos):
    """
    Read the header and the counts data of a selected ADC
    Input:
    - datas        : path of the .mpa file
    - adc_num      : ADC to analyse 
    - adcs_flag_pos: indexes of the cells in the "datas" list containing the first row
                     of the ADCs' headers
    - data_flag_pos: indexes of the cells in the "datas" list containing the first row
                     of the ADCs' data
    Output: 
    - adc_header     : Header of the ADC (dictionary) 
    - adc_data       : Counts read by the ADC
    - adc_data_errors: Errors on the counts (evaluated as the square root of the counts
                                            read by the ADC)
    """

    raw_adc_header = datas[adcs_flag_pos[adc_num-1]:adcs_flag_pos[adc_num]]
    adc_header = {}

    for val in raw_adc_header:
        splited_val = val.split('=')
        if len(splited_val) == 2:
            try:
                adc_header[splited_val[0]] = float(splited_val[1])
            except:
                adc_header[splited_val[0]] = splited_val[1]

    raw_adc_data    = datas[data_flag_pos[adc_num-1]+1:data_flag_pos[adc_num]]
    adc_data        = np.array([float(val) for val in raw_adc_data])
    adc_data_errors = np.sqrt(adc_data)

    return adc_header, adc_data, adc_data_errors

def calibrate(adc_header):
    """
    Calibrate the ADC data using the calibration factors saved in the ADC header
    Input:
    - adc_header     : Header of the ADC (dictionary) 
    Output: 
    - channels: Channels of the ADC
    - energies: Channels as calibrated energies
    """
    calibration_coeffs = [adc_header['caloff'], adc_header['calfact'], adc_header['calfact2'], adc_header['calfact3']]
    channels           = np.array(range(int(adc_header['range'])))
    energies           = calibration_coeffs[0] + calibration_coeffs[1]*channels + calibration_coeffs[2]*channels**2 + calibration_coeffs[3]*channels**3

    return channels, energies


def configure_ADC():
    """
    Change the ADC to analyse
    Output: 
    - adc_num: ADC to analyse 
    """
    cont = True

    while cont:
        
        print('Which ADC data do I have to analyse? (1,2,3,4; 0 to quit)')
        try:
            adc_num = int(input(''))
            if adc_num == 0 or 1 <= adc_num <= 4:
                cont = False
            else:
                print('Invalid ADC number! ADCs are numbered from 1 to 4. Please, retry\n')
        except:
            print('Invalid character in selection! Please, retry\n')

    print('\nDone! Selected ADC: ', adc_num)

    return adc_num

def configure_scale():
    """
    Change the scale used to plot the data (linear or log)
    Output: 
    - log_scale: If True, plot in log scale. Otherwise, plot in linear scale
    """
    cont = True

    while cont:

        print('Do you want the counts to be in log scale? (y/n, 0 to quit): ')
        sel = input('')
        
        if sel == '0':
            cont = False
        elif sel == 'y' or sel == 'Y':
            log_scale = True
            cont = False
        elif sel == 'n' or sel == 'N':
            log_scale = False
            cont = False
        else:
            print('Invalid selection! Please, retry\n')

    if log_scale:
        print('\nDone! Log scale selected')
    else:
        print('\nDone! Linear scale selected')
    
    return log_scale