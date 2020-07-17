import json
import os
import datetime
import logging
import shutil
from zipfile import ZipFile


'''
Script de Rotate Logs

Informações usadas abaixo vem do arquivo config.json que se encontra no mesmo diretório

    "paths": [{
        "robot1":"./logs/" ---- O caminho onde serão buscados os logs
    }],
    "extensions": ".log|.html", ---- ainda não implementado
    "output":[{ 
        "robot1":"C:\\OutputLogs\\", --- O caminho onde serão salvos os logs
        "robot2":""

    }]

'''
def setup_log():
    execution_time = datetime.datetime.now()
    execution_time = execution_time.strftime("%Y%m%d%H%M%S")

    logging.basicConfig(filename=f"Execution-{execution_time}.log", filemode='w', format ='%(asctime)s - %(levelname)s  - %(message)s', level=logging.INFO)
    
def read_config():
    
    #Rotina que le o json de configuração e extrai os dicionários com as informações
    logging.info("Buscando configurações")
    with open("./config.json") as f:
        full_json = json.load(f)
    robot_config = {}
    robot_outputs = {}
    for line in full_json['paths']:
        for key in line:
            robot_config[key] = line[key]
    robot_config["extensions"] = full_json['extensions']
    for line in full_json['output']:
        for k in line:
            robot_outputs[k] = line[k]

    return robot_config, robot_outputs
        

def rotate_log(path,output):
    logging.info("Iniciando varredura")
    last_date = ""
    files_to_be_zipped = []
    #varre cara arquivo do diretório buscando pela extensão definida abaixo
    try:
        for file in os.listdir(path):
            if file.endswith(".log"):
                now = datetime.datetime.now()
                full_filePath = f"{path}{file}"

                logging.info(f"Processando -> {full_filePath}")

                date = get_creation_date(full_filePath)
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                
                #
                #Compara se a data de criação do arquivo é menor que a data atual. Se sim, inicia o processo de compactação
                #
                if now>date:
                    str_date = f"{date.year}-{date.month}-{date.day}"
                    str_date = datetime.datetime.strptime(str_date,"%Y-%m-%d")
                    str_date = str_date.strftime("%Y-%m-%d")
                    if last_date == "":
                        last_date = str_date
                        files_to_be_zipped.append(full_filePath)
                        continue
                    elif last_date == str_date:
                        files_to_be_zipped.append(full_filePath)
                    else:
                        #print(files_to_be_zipped)
                        logging.info(f"Compactando batch de logs - Data: {last_date} - Diretório: {output}")
                        zip_files(last_date,files_to_be_zipped,output)
                        files_to_be_zipped=[]
                        last_date = str_date 
                        files_to_be_zipped.append(full_filePath)
        if len(files_to_be_zipped) >0:
            logging.info(f"Compactando batch de logs - Data: {last_date} - Diretório: {output}")
            zip_files(last_date,files_to_be_zipped,output)   
    except Exception as e:
        logging.error("Exceção ocorreu: ",exc_info=True)

    finally:
        logging.info("============== Fim da Execução ============== ")

def get_creation_date(file_path):
    #Verifica a data de criação do arquivo
    #usar getmtime para data de modificação
    try:
        creation_date = os.path.getmtime(file_path)
        modification_time = datetime.datetime.fromtimestamp(creation_date).strftime("%Y-%m-%d %H:%M:%S")
        return modification_time
    except FileNotFoundError :
        return (f"File {file_path} not found")    
    except Exception as e:
        print(e)

def zip_files(str_date,files_list,output_folder):
    try:
        with ZipFile(f"{str_date}.zip","w",allowZip64 = True) as zip:
            for files in files_list:
                zip.write(files)
        shutil.move(f"{str_date}.zip",f"{output_folder}{str_date}.zip")        
        #os.rename(f"{str_date}.zip",f"{output_folder}{str_date}.zip")        
        delete_old_files(files_list)
    except Exception as e:
        logging.error("Exceção Ocorreu: ", exc_info=True)
        #print(f"An error happen {e}")

def delete_old_files(files_list):
    try:
        for f in files_list:
            os.remove(f)
    except Exception as e:
        logging.error("Exceção Ocorreu: ", exc_info=True)

if __name__ == "__main__":
    setup_log()
    logging.info("Iniciando compressão")
    robot_paths, robot_outputs = read_config()
    for keys in robot_paths.keys():
        if keys != "extensions":
            rotate_log(path=robot_paths[keys],output=robot_outputs[keys])
