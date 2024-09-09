import os
import requests
import time
import json
import subprocess
from urllib.parse import quote

config_json_file = 'config.json'
info_json_file = 'info.json'
test_host = 'www.baidu.com'
entrance_host = "http://123.123.123.123"


def get_now_time():
    t = time.localtime()
    return t.tm_hour


def check_network_activity(host):
    def ping(host_):
        try:
            output = subprocess.check_output("curl "+host_, shell=True)
            if output.decode('utf-8')[0:15] == '<!DOCTYPE html>':
                return 1
            elif output.decode('utf-8')[0:31] == '<script>top.self.location.href=':
                return 2
            else:
                return 0
        except subprocess.CalledProcessError:
            return 0
    return ping(host)


def check_login_activity():
    return


def get_services(ePortalUrl, queryString):
    services = requests.get(
        ePortalUrl + "InterFace.do?method=getServices&queryString=" + queryString)
    return services.content.decode('utf-8')


def login(ePortalUrl, userId, password, service, queryString, passwordEncrypt):
    login_url = ePortalUrl + "InterFace.do?method=login"
    login_url += "&userId=" + userId
    login_url += "&password=" + password
    login_url += "&service=" + service
    login_url += "&queryString=" + queryString
    login_url += "&operatorPwd="
    login_url += "&operatorUserId="
    login_url += "&validcode="
    login_url += "&passwordEncrypt=" + passwordEncrypt
    login_ = requests.get(login_url)
    return login_.content.decode('utf-8')


def get_info(ePortalUrl, userIndex):
    info_url = ePortalUrl + "InterFace.do?method=getOnlineUserInfo"
    info_url += "&userIndex=" + userIndex
    info_ = requests.get(info_url)
    return info_.content.decode('utf-8')


def login_main():
    test_network_flag = check_network_activity(test_host)
    entrance_network_flag = check_network_activity(entrance_host)
    if (test_network_flag == 1):
        print(">INFO Already linked.")
    elif (test_network_flag == 2) or (entrance_network_flag == 2):
        ePortalUrl_entrance = requests.get(entrance_host)
        ePortalUrl_main = ePortalUrl_entrance.text[32:-12]
        ePortalUrl = ePortalUrl_main[0:25]
        queryString = quote(quote(ePortalUrl_main[35:]))
        services_json = json.loads(get_services(ePortalUrl, queryString))
        services_list_json = json.loads(services_json['services'])
        for i in range(len(services_list_json)):
            if (serviceShowName == services_list_json[i]['serviceShowName']):
                serviceName = quote(
                    quote(services_list_json[i]['serviceName']))
                break
        login_info_json = login(ePortalUrl, userId, password,
                                serviceName, queryString, passwordEncrypt)
        login_info = json.loads(login_info_json)
        print(login_info)
        if (login_info['result'] == "fail"):
            print(">ERROR Login Fail")
        elif (login_info['result'] == "success"):
            print(">INFO Login success")
            userIndex = login_info['userIndex']
            config_data['userIndex'] = userIndex
            os.remove(config_json_file)
            with open(config_json_file, 'w') as file:
                file.write(json.dumps(config_data))
            user_info = json.loads(get_info(ePortalUrl, userIndex))
            with open(info_json_file, 'w') as file:
                file.write(json.dumps(user_info))
    else:
        print(">ERROR Unable to entrance.")


if __name__ == "__main__":
    print('----- Programme Begin -----')

    # init
    with open(config_json_file, 'r') as file:
        config_data = json.load(file)
    handle_start = int(config_data['handle_start'])
    loop_time = config_data['loop_time'].split(',')
    userId = config_data['userId']
    password = config_data['password']
    serviceShowName = config_data['serviceShowName']
    passwordEncrypt = config_data['passwordEncrypt']

    # print
    print('--- Config ---')
    print(f"handle_start: {handle_start}")
    print(f"loop_time: {loop_time}")
    print(f"userId: {userId}")
    print(f"password: {password}")
    print(f"serviceShowName: {serviceShowName}\n")

    # var
    global ePortalUrl
    global queryString
    global serviceName
    global userIndex

    # main
    while (True):
        login_main()
        delay_time = int(loop_time[0])*3600 + \
            int(loop_time[1])*60+int(loop_time[2])+5
        h = get_now_time()
        if (handle_start == 1):
            if (h > 2) and (h < 5):
                print(">WARN Touch time wall, auto exit untill handle start.")
                exit
            else:
                print(">INFO Time wall check pass.")
        print(
            f">INFO Login bash will delay {delay_time} seconds to next loop.")
        time.sleep(delay_time)
