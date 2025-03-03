from multiprocessing import Pool, cpu_count

def generate_watermark(...):
    # ... (其他代码不变)
    with Pool(processes=cpu_count()) as pool:
        pool.starmap(process_single_image_wrapper,
                    [(input_path, os.path.join(output_folder, os.path.basename(input_path)), config, npy_data, quality)
                     for input_path in image_files])

def process_single_image_wrapper(args):
    return process_single_image(*args)