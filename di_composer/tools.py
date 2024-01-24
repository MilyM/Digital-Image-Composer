import os
from osgeo import gdal
import numpy as np

CCFG_EXT = 'ccfg'

# szukanie bandów
def find_bands(path: str, file_ext: str, by_ext_search: bool) -> list:
    """Szukana plików w folderze)

    Args:
        path (str): scieżka do folderu przeszukiwanego
        file_ext (str): rozszerzenieie pliku
        by_ext_search (bool): szukanie pliku po rozszerzeniu (true), wszystkie pliki w podanej lokalizacji(false)

    Returns:
        list: znalezione pliki
    """    
    files = []
    for file in os.listdir(path): 
        if by_ext_search:
            if file.endswith(f'.{file_ext}'):
                files.append(file)
        else:
            files.append(file)

    return files

# tworzenie pliku konfiuracyjnego
def create_ccfg(bands: dict, filename: str, data_path: str, output_path: str) -> None:
    """tworzy plik konfigracyjny ccfg

    Args:
        bands (dict): słownik z nazwami plików dla każdego kanału (value), oraz z wyznaczonymi skrótami (key)
        filename (str): nazwa pliku ccfg
        data_path (str): docelowa lokalizacja folderu z danymi (monochromatyczne zdcięcia)
        output_path (str): docelowa lokalizacja zapisu pliku ccfg
    """    
    full_path = f'{output_path}/{filename}.{CCFG_EXT}'

    file = open(full_path, 'w')
    file.write(f'{data_path}\n')
    file.write(f'{output_path}\n')

    for key, value in bands.items():
        file.write(f'{value};{key}\n')
    
    file.close()

# otwieranie pliku konfiguracyjnego    
def open_ccfg(path: str)-> list:
    """otwiera plik ccfg i zwraca scieżki dostepu oraz zapisu, tworzy słownik na podstawie wartości w pliku

    Args:
        path (str): scieżka do pliku ccfg

    Returns:
        list: lista z elementami:
        data_path(str): scieżka ze zdjęciami monochromatycznymi
        output_path(str): scieżka zapisu kompozycji
        bands(dict): słownik ze skrótami (key), nazwy plików zdjęciowych(value)
    """    
    bands = {}
    file = open(path, 'r')

    lines = [line.strip() for line in file.readlines()] 
    lines_size = len(lines)

    data_path = lines[0]
    output_path = lines[1]

    for i in range(2, lines_size):
        value, key = lines[i].split(';')
        print(key, value)
        bands[key] = value

    return data_path, output_path, bands


# tworzenie kompozycji
def create_composition(bands_filenames: list, names: list,  bands_path:str, output_path: str, output_filename: str, output_extension: str, output_driver: str, pixel_data_type) -> str:
    """tworzenie kompozcyji barwnej z podanych zdjęc chromatycznych

    Args:
        bands_filename (list): nazwy plików z których będzie tworzona kompozycja barwna
        names (list): opisy zdjęć
        bands_path (str): folder lokaliazcji zdjęć
        output_path (str): folder zapisu nowej kompozycji
        output_filename (str): nazwa pliku nowej kompozycji
        output_extension (str): rozszerzenie pliku nowej kompozycji
        output_driver (str): silnik tworzenia kompozycji, gdal
        pixel_data_type (): typ danych z biblioteki gdal

    Returns:
        str: pełna scieżka do utworzonej kompozycji
    """
    bands_size = len(bands_filenames)
    bands = []

    for band_path in bands_filenames:
        print(band_path)
        band = gdal.Open(f'{bands_path}/{band_path}')
        bands.append(band)

    projection = bands[0].GetProjection()
    transform = bands[0].GetGeoTransform()
    x_pix = bands[0].RasterXSize
    y_pix = bands[0].RasterYSize

    driver = gdal.GetDriverByName(output_driver)
    output = f'{output_path}/{output_filename}.{output_extension}' 
    composition = driver.Create(output, x_pix, y_pix, bands_size, pixel_data_type)
    composition.SetProjection(projection)
    composition.SetGeoTransform(transform) 

    for i in range(bands_size):
        composition_band = bands[i].GetRasterBand(1).ReadAsArray()
        composition.GetRasterBand(i+1).WriteArray(composition_band)
        composition.GetRasterBand(i+1).SetDescription(names[i])
    composition = None
    
    return output


def create_composition_none(bands_filename: list, names: list,  bands_path:str, output_path: str, output_filename: str, output_extension: str, output_driver: str, pixel_data_type) -> str:
    """tworzenie kompozcyji barwnej z podanych zdjęc chromatycznych z mozliwoscia tworzenia zerowych macierzy (kanałow wypełnionych zerami)

    Args:
        bands_filename (list): nazwy plików z których będzie tworzona kompozycja barwna
        names (list): opisy zdjęć
        bands_path (str): folder lokaliazcji zdjęć
        output_path (str): folder zapisu nowej kompozycji
        output_filename (str): nazwa pliku nowej kompozycji
        output_extension (str): rozszerzenie pliku nowej kompozycji
        output_driver (str): silnik tworzenia kompozycji, gdal
        pixel_data_type (): typ danych z biblioteki gdal

    Returns:
        str: pełna scieżka do utworzonej kompozycji
    """
    bands_size = len(bands_filename)
    bands = []
    good_band_index = 0


    for band_path in bands_filename:
        if band_path != None: 
            print(band_path)
            band = gdal.Open(f'{bands_path}/{band_path}')
            bands.append(band)
            main_band = band
        else: 
            bands.append(None)

    projection = bands[good_band_index].GetProjection()
    transform = bands[good_band_index].GetGeoTransform()
    x_pix = bands[good_band_index].RasterXSize
    y_pix = bands[good_band_index].RasterYSize

    driver = gdal.GetDriverByName(output_driver)
    output = f'{output_path}/{output_filename}.{output_extension}' 
    composition = driver.Create(output, x_pix, y_pix, bands_size, pixel_data_type)
    composition.SetProjection(projection)
    composition.SetGeoTransform(transform) 

    for i in range(bands_size):
        if bands[i] != None:
            composition_band = bands[i].GetRasterBand(1).ReadAsArray()
            composition.GetRasterBand(i+1).WriteArray(composition_band)
            composition.GetRasterBand(i+1).SetDescription(names[i])
        else:
            composition_band = bands[good_band_index].GetRasterBand(1).ReadAsArray()
            composition.GetRasterBand(i+1).WriteArray(composition_band)
            composition.GetRasterBand(i+1).Fill(0)
            composition.GetRasterBand(i+1).SetDescription(names[i])
    composition = None
    
    return output


def read_fastmode(filename: str) -> dict:
    """wczytywanie pliku z danymi do fast mode

    Args:
        filename (str): nazwa pl

    Returns:
        dict: słownik zawierajacy dane kompozycjami
    """    
    fast_mode_dict = {}
    path = os.path.join( os.path.dirname(__file__), filename)
    file = open(path, 'r')

    lines = [line.strip() for line in file.readlines()] 
    lines_size = len(lines)

    for i in range(lines_size):
        satelite, desc, b1, b2, b3 = lines[i].split(';')
        tmp = [satelite, desc, b1, b2, b3]
        print(tmp)
        key = f'{satelite}: {desc}: {b1};{b2};{b3}'
        fast_mode_dict[key] = [desc, b1, b2, b3]

    
    return fast_mode_dict
        

