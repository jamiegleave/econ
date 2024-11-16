import os
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime


def get_corporate_bond_holdings(url,path):
    """
    Scrapes holdings data for Vanguard USD Corporate Bond UCITS ETF from Vanguard UK website.
    
    Returns:
        pandas.DataFrame: ETF holdings data
    """
    #url = "https://www.vanguard.co.uk/professional/product/etf/bond/9594/usd-corporate-bond-ucits-etf-usd-accumulating"
    #path = r"C:\Users\jamie\OneDrive\Python\Py_24\Git_master\econ\VDPA"

    path_len = len(os.listdir(path))

    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  # Set a larger window size
    options.add_experimental_option("prefs", {
        "download.default_directory": path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
        })
    
    # Initialize webdriver
    print("Initializing Chrome webdriver...")
    driver = webdriver.Chrome(options=options)
    
    # Navigate to the page
    print(f"Navigating to {url}...")
    driver.get(url)
    
    # Handle cookie consent #1
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_button.click()
        time.sleep(2)
    except TimeoutException:
        print("First cookie banner found or already accepted")

    # Handle cookie consent #2 
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//europe-core-cookie-consent-dialog//button[span[contains(text(), 'agree')]]"))    #//[tagname]//[button][index]
        )
        cookie_button.click()
        time.sleep(2)
    except TimeoutException:
        print("First cookie banner found or already accepted")
    
    # Wait for and locate the holdings table
    print("Extracting holdings data...")
    holdings_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//europe-core-fund-holdings//button[1]"))    #//[tagname]//[button][index]
        )
    holdings_button.click()
    
    WebDriverWait(driver,timeout=2).until(
        lambda x: len(os.listdir(path)) > path_len and 
        True not in ['.crdownload' in i for i in os.listdir(path)]
    )
    print('File downloaded')

    driver.quit()


def weighted_quantile(values, quantiles, sample_weight=None, 
                      values_sorted=False, old_style=False):
    """ Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of
        initial array
    :param old_style: if True, will correct output to be consistent
        with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), \
        'quantiles should be in [0, 1]'

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]

    weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(sample_weight)
    return np.interp(quantiles, weighted_quantiles, values)