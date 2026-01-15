import urllib.request
from urllib.error import HTTPError, URLError
import json
import hashlib
import ast

from app.utils.setting_loader import AppConfig
from app.utils.utils import convert_to_unsigned_preserve_case

LOGIN_URL = 'https://egw.baohiemxahoi.gov.vn/api/token/take'
CHECK_BHYT_URL = 'https://egw.baohiemxahoi.gov.vn/api/egw/KQNhanLichSuKCB2024'

def login(username, password):
    encode_pwd = hashlib.md5(password.encode()).hexdigest()
    payload = {"username": username, "password": encode_pwd}

    # Convert dictionary to a JSON string and then to bytes
    json_data = json.dumps(payload).encode('utf-8')
    # print(json_data)

    # Build the request object
    req = urllib.request.Request(LOGIN_URL, data=json_data, method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')

    login_info = {
        'access_token': None,
        'id_token': None,
        'username': username,
        'password': ''
    }

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        # print(f"Status: {response.status}")
        # print(result)

        if result.get('maKetQua', '0') == '200':
            token = result.get('APIKey')
            login_info['access_token'] = token.get('access_token')
            login_info['id_token'] = token.get('id_token')
            login_info['username'] = username
            login_info['password'] = encode_pwd

    return login_info

def check_bhyt(
        username,
        password,
        maThe = '',
        hoTen ='',
        ngaySinh='',
        hoTenCb='',
        cccdCb='',
):
    try:
        credential = login(username, password)
        url = (f"{CHECK_BHYT_URL}?username={credential['username']}"
               f"&password={credential['password']}"
               f"&token={credential['access_token']}"
               f"&id_token={credential['id_token']}")
        # print(url)

        payload = {
            "maThe": maThe,  # Mã bhxh hoặc mã thẻ BHYT
            "hoTen": hoTen,  # Họ tên có thể là k dấu
            "ngaySinh": ngaySinh,  # ngày tháng năm sinh hoặc năm sinh, eg: 01012026 hoac 2026
            "hoTenCb": hoTenCb,  # họ tên cán bộ tra cứu(có thể k đấu)
            "cccdCb": cccdCb,  # số cccd cán bộ tra cứu đã được cấp quyền
        }

        # Convert dictionary to a JSON string and then to bytes
        json_data = json.dumps(payload).encode('utf-8')
        # print(json_data)

        # Build the request object
        req = urllib.request.Request(url, data=json_data, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            # print(f"Status: {response.status}")
            # print(result)
            return result
    except HTTPError as e:
        # Lỗi 401, 404, 500... sẽ rơi vào đây
        # print(f"Lỗi HTTP: {e.code}")  # Sẽ in ra 401

        # Đôi khi Server vẫn trả về JSON mô tả lỗi trong Body
        error_body = e.read().decode('utf-8')
        # print(f"Nội dung lỗi từ Server: {error_body}")

        # if e.code == 401:
            # print("Xác thực thất bại: Kiểm tra lại username/password hoặc Token.")
        return error_body
    except URLError as e:
        # Lỗi kết nối (sai URL, không có internet, server sập)
        # print(f"Lỗi kết nối: {e.reason}")
        response = {"maKetQua":"700"}
        return response

def thong_tuyen_bhyt(maThe, hoTen, namSinh):
    _hoTen = convert_to_unsigned_preserve_case(hoTen)
    response = check_bhyt(AppConfig.USERNAME_THONG_TUYEN_BHYT,
                          AppConfig.PASSWORD_THONG_TUYEN_BHYT,
                          maThe, _hoTen, namSinh,
                          AppConfig.HO_TEN_CAN_BO,
                          AppConfig.CCCD_CAN_BO)
    return response