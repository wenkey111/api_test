#DummyJSON
import requests
import pytest
import allure
import os
import csv

BASE_API_URL = "https://dummyjson.com"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "login_api_data.csv")


def get_test_data():
    data = []
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"测试数据文件不存在：{TEST_DATA_PATH}")

    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_headers = ["username", "password", "expect_code", "expect_keyword", "case_desc"]
        if not all(header in reader.fieldnames for header in required_headers):
            raise ValueError(f"CSV缺少必要表头：{required_headers}")

        for row in reader:
            data.append((
                row["username"],
                row["password"],
                int(row["expect_code"]),
                row["expect_keyword"],
                row["case_desc"]
            ))
    return data


@allure.feature("在线接口测试-登录模块")
class TestOnlineLoginAPI:
    @allure.story("登录接口功能验证")
    @allure.title("{case_desc}")
    @pytest.mark.parametrize("username, password, expect_code, expect_keyword, case_desc", get_test_data())
    def test_login_api(self, username, password, expect_code, expect_keyword, case_desc):
        req_data = {}
        if username:
            req_data["username"] = username
        if password:
            req_data["password"] = password
        with allure.step("1. 构造登录接口请求"):
            login_url = f"{BASE_API_URL}/user/login"
            headers = {"Content-Type": "application/json"}
            allure.attach(f"请求地址：{login_url}\n请求参数：{req_data}", name="请求信息")

        with allure.step("2. 发送登录接口请求"):
            try:
                response = requests.post(
                    url=login_url,
                    json=req_data,
                    headers=headers,
                    timeout=10,
                    allow_redirects=False
                )
                print(f"\n【用例】：{case_desc}")
                print(f"【状态码】：{response.status_code}")
                print(f"【响应内容】：{response.json()}")
            except Exception as e:
                pytest.fail(f"接口请求/解析异常：{str(e)}", pytrace=False)

        with allure.step("3. 验证接口响应结果"):
            assert response.status_code == expect_code, \
                f"状态码断言失败！预期：{expect_code}，实际：{response.status_code}"

            response_json = response.json()
            if expect_code == 200:
                assert "accessToken" in response_json, \
                    f"登录成功但未返回accessToken！响应：{response_json}"
            else:
                assert expect_keyword in response_json.get("message", ""), \
                    f"错误信息断言失败！预期包含：{expect_keyword}，实际：{response_json.get('message', '无错误信息')}"

            allure.attach(f"状态码：{response.status_code}\n响应内容：{response_json}", name="响应信息")