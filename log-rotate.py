import json
import os
import datetime
from zipfile import ZipFile, LargeZipFile

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

def read_config():
    
    #Rotina que le o json de configuração e extrai os dicionários com as informações

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
    last_date = ""
    files_to_be_zipped = []
    #varre cara arquivo do diretório buscando pela extensão definida abaixo
    for file in os.listdir(path):
        if file.endswith(".log"):
            now = datetime.datetime.now()
            full_filePath = f"{path}{file}"
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
                    zip_files(last_date,files_to_be_zipped,output)
                    files_to_be_zipped=[]
                    last_date = str_date 
                    files_to_be_zipped.append(full_filePath)
    if len(files_to_be_zipped) >0:
        zip_files(last_date,files_to_be_zipped,output)   

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
        os.rename(f"{str_date}.zip",f"{output_folder}{str_date}.zip")        
        delete_old_files(files_list)
    except Exception as e:
        print(f"An error happen {e}")

def delete_old_files(files_list):
    for f in files_list:
        os.remove(f)

if __name__ == "__main__":
    robot_paths, robot_outputs = read_config()
    for keys in robot_paths.keys():
        if keys != "extensions":
            rotate_log(path=robot_paths[keys],output=robot_outputs[keys])
