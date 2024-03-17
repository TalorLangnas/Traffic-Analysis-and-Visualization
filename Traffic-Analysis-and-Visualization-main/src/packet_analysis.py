import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


def plot_packet_length_by_time(file_with_name):
    """
    Plot packet length over time from CSV files.

    """
    for csv_file in file_with_name:
        file_path = csv_file[0]
        title = csv_file[1]
        if title == 'textGroupAndSpotify':
            plot_all_protocols('../resources/csv_files/textGroupAndSpotify.csv')
        else:
            data_frame = pd.read_csv(file_path)

            # Create a new figure and axis
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Packet Length (Bytes)')
            ax.set_title(title)

            # Create a bar plot of packet lengths
            ax.bar(data_frame['Time'], data_frame['Length'], color='blue', width=0.1, alpha=0.5, edgecolor='blue')
            plt.grid(True)

            save_plot_to_path(fig, f'IMD_{title}')


def plot_all_protocols(csv_path):
    """
    :param csv_path: path of csv file contains different types of protocols and plots
                    compare - based graph shows traffic for each.
                    the plot would save into plots_png dir
    """
    df = pd.read_csv(csv_path)
    protocols = df['Protocol'].unique()

    fig, ax = plt.subplots(figsize=(10, 5))

    for protocol in protocols:
        protocol_df = df[df['Protocol'] == protocol]

        # Create a bar plot of packet lengths
        ax.bar(protocol_df['Time'], protocol_df['Length'], width=0.8, alpha=0.8, label=protocol)

    ax.set_title('Plot Packet Length by Time for each Protocol', fontsize=20)
    ax.set_xlabel('Time (seconds)', fontsize=14)
    ax.set_ylabel('Packet Length (Bytes)', fontsize=14)
    plt.grid(True)
    ax.legend()

    save_plot_to_path(fig, 'textAndSpotify')


def get_csv_files_with_names():
    """
    Get a list of CSV files with their names (without extension) from a directory.

    :return: A list of tuples containing file paths and names.
    """
    files_list = []

    for file in os.listdir('../resources/csv_files'):
        if file.endswith(".csv"):
            file_path = os.path.join('../resources/csv_files', file)
            file_name_without_extension = os.path.splitext(file)[0]
            files_list.append((file_path, file_name_without_extension))

    return files_list


def calculate_delay_times(files_with_names):
    """
    Read CSV files and calculate delay times for each file.

    :param files_with_names: A list of tuples containing file paths and names.
    :return: A list of tuples containing DataFrames and group names.
    """
    data_frames_list = []
    for csv_file in files_with_names:
        data_frame = pd.read_csv(csv_file[0])
        group_name = csv_file[1]
        delays = np.diff(data_frame['Time'])
        delays = np.append(delays, 0)
        data_frame['Delay_Time'] = delays
        data_frames_list.append((data_frame, group_name))

    return data_frames_list


def fit_exponential_distribution(lambda_param, max_delay, scale):
    """
    Fit exponential distribution and return arrays for x and y values..

    :param lambda_param: Mean of delay times.
    :param max_delay: Maximum delay time.
    :return: Arrays for x and y values of the distribution.
    """
    x = np.linspace(0, max_delay, num=1000)
    y = scale * lambda_param * np.exp(-lambda_param * x)

    return x, y


# Plot Probability Density Function (PDF) of delay times.
def plot_delay_pdf(data_frame, group_name):
    """
    Plot Probability Density Function (PDF) of delay times.

    :param data_frame: DataFrame containing delay time information.
    :param group_name: Name of the data group.
    """

    # mean_delay = np.mean(data_frame['Delay_Time'])
    max_delay = data_frame['Delay_Time'].max()
    lambda_parameter = 1 / np.mean(data_frame['Delay_Time'])
    rng = int(np.ceil(max_delay))
    bin_step = np.arange(0, rng)
    pdf, bin_pdf = np.histogram(data_frame['Delay_Time'], bins=bin_step, density=True)
    pdf_ = np.append(pdf, 0)

    # calculate scale factor for exponential_distribution with values between [0, 1]
    scale = max(pdf_) / lambda_parameter * np.exp(-lambda_parameter * bin_pdf[np.argmax(pdf_)])

    x, y = fit_exponential_distribution(lambda_parameter, max_delay, scale)

    fig, ax = plt.subplots(figsize=(10, 4))

    # Plot the PDF and the fitted exponential distribution
    ax.step(bin_pdf, pdf_, label='PDF')
    ax.plot(x, y, label='exponential distribution', alpha=0.4, color='red')

    ax.set_title(group_name)
    ax.set_xlabel('Inter Message Delays (Seconds)')
    ax.set_ylabel('PDF')
    ax.legend()
    plt.grid(True)

    save_plot_to_path(fig, f'PDF_{group_name}')


def plot_all_delay_pdfs(data_frame):
    """
    Plot PDF for all data groups.

    :param data_frame: A list of tuples containing DataFrames and group names.
    """
    for data_frame in data_frame:
        plot_delay_pdf(data_frame[0], data_frame[1])


def get_ccdf(data_frame):
    """
    Generate list of tuples into CCDF graph, values range and tutel of graph

    :param data_frame is list of tuples (df,group_name)
    :returns ccdf_val is Complementary CDF of Y values
            x_values
            group_name is name of csv file as graph title
    """
    df = data_frame[0]
    group_name = data_frame[1]
    packet_length = df['Length']
    packet_length = np.sort(packet_length)
    y_values = np.arange(1, len(packet_length) + 1) / len(packet_length)
    x_values = packet_length/max(packet_length)
    ccdf_val = 1 - y_values

    return ccdf_val, x_values, group_name


def cdf_list(data_frames):
    """"
    Calculate CCDF, normalized bins-range and graph title

    :param data_frames is alist of data frames from csv file
    :return ccdfs_list is triples of parameters for each file
    """
    ccdfs_list = []

    for dataFrame in data_frames:
        ccdf_val, x_values, group_name = get_ccdf(dataFrame)
        ccdfs_list.append((ccdf_val, x_values, group_name))

    return ccdfs_list


def plot_CCDF(cdfs_list):
    """"
    Plots CCDF of all the list in one axes
    :param cdfs_list: a list of cdf, bins_normalized, group_name
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    plt.yscale('log')

    for cdf in cdfs_list:
        ccdf_ = cdf[0]
        x_values = cdf[1]
        group_name = cdf[2]

        # Plot the PDF and the fitted exponential distribution
        ax.plot(x_values, ccdf_, label=group_name)

    ax.set_title(' Complementary CDF of IM Size distributions for different types of messages')
    ax.set_xlabel('Normalized message sizes to their maximum')
    ax.set_ylabel('CCDF')
    plt.grid(True)
    ax.legend()
    save_plot_to_path(fig, "ccdf")


def save_plot_to_path(fig, name):
    """
    Save a Matplotlib figure to a specified path with a given name.

    :param fig: Matplotlib figure object to be saved.
    :param name: Desired file name (including extension) for the plot.
    """
    # Combine the path and name to form the full file path
    full_file_path = os.path.join('../plots_png', name)

    # Save the plot to the specified path and name
    fig.savefig(full_file_path)

    # Close the plot to prevent it from displaying on the screen
    plt.close()


def delete_png_files():
    directory_path = '../plots_png'
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path) and item.lower().endswith('.png'):
            os.remove(item_path)



def main():
    delete_png_files()

    files_with_name = get_csv_files_with_names()
    data_frames = calculate_delay_times(files_with_name)
    plot_all_delay_pdfs(data_frames)
    plot_packet_length_by_time(files_with_name)
    CDF_list = cdf_list(data_frames)
    plot_CCDF(CDF_list)


if __name__ == '__main__':
    main()
