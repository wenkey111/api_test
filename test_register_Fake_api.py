import requests
import pytest
import allure
import os
import csv

BASE_API_URL = "https://fakestoreapi.com"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "register_Fake_api_data.csv")


def get_test_data():
    data = []
    # 检查文件是否存在
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"测试数据文件不存在：{TEST_DATA_PATH}")

    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # 检查CSV表头是否完整
        required_headers = ["username", "email", "password", "expect_code", "expect_keyword", "case_desc"]
        if not all(header in reader.fieldnames for header in required_headers):
            raise ValueError(f"CSV缺少必要表头：{required_headers}")
        # 读取每一行测试数据
        for row in reader:
            data.append((
                row["username"],
                row["email"],
                row["password"],
                int(row["expect_code"]),
                row["expect_keyword"],
                row["case_desc"]
            ))
    return data

@allure.feature("FakeStore电商平台-注册模块")
class TestFakeStoreRegisterAPI:
    @allure.story("用户注册接口功能验证（真实校验）")
    @allure.title("{case_desc}")
    @pytest.mark.parametrize("username, email, password, expect_code, expect_keyword, case_desc", get_test_data())
    def test_register_api(self, username, email, password, expect_code, expect_keyword, case_desc):
        # 构造注册请求参数（仅传非空字段）
        req_data = {}
        if username:
            req_data["username"] = username
        if email:
            req_data["email"] = email
        if password:
            req_data["password"] = password

        with allure.step("1. 构造注册接口请求"):
            register_url = f"{BASE_API_URL}/users"
            headers = {"Content-Type": "application/json"}
            allure.attach(f"请求地址：{register_url}\n请求参数：{req_data}", name="请求信息")

        with allure.step("2. 发送注册接口请求"):
            try:
                #发送POST请求（禁用重定向，确保响应纯净）
                response = requests.post(
                    url=register_url,
                    json=req_data,
                    headers=headers,
                    timeout=10,
                    allow_redirects=False
                )
                # 打印调试信息，方便排查
                print(f"\n【用例】：{case_desc}")
                print(f"【状态码】：{response.status_code}")
                print(f"【响应内容】：{response.json()}")
            except Exception as e:
                pytest.fail(f"接口请求/解析异常：{str(e)}", pytrace=False)

        with allure.step("3. 验证注册接口响应结果"):
            # 第一步：断言状态码（核心，匹配预期）
            assert response.status_code == expect_code, f"状态码断言失败！预期：{expect_code}，实际：{response.status_code}"
            response_json = response.json()
            # 第二步：分场景断言（贴合接口真实返回）
            if expect_code == 201: #成功场景
                #成功必须返回id字段（接口自动生成）
                assert "id" in response_json, f"注册成功但未返回用户ID！响应：{response_json}"
                #验证传入的参数和返回一致
                assert response_json.get("username") == username, f"username不匹配！预期：{username}，实际：{response_json.get('username')}"
                assert response_json.get("email") == email, f"email不匹配！预期：{email}，实际：{response_json.get('email')}"

            elif expect_code == 400:  # 失败场景
                #失败必须返回error字段，且包含预期关键词
                assert "error" in response_json, f"注册失败但未返回错误信息！响应：{response_json}"
                assert expect_keyword in response_json["error"], \
                    f"错误信息断言失败！预期包含：{expect_keyword}，实际：{response_json['error']}"

            #把响应信息附加到Allure报告
            allure.attach(f"状态码：{response.status_code}\n响应内容：{response_json}", name="响应信息")

# if __name__ == "__main__":
#     pytest.main([__file__, "--alluredir", "./allure-results", "-v", "-s"])
#     if os.system("allure --version >nul 2>&1") == 0:
#         os.system(f"allure serve ./allure-results")