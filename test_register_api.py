#DummyJSON
import requests
import pytest
import allure
import os
import csv

BASE_API_URL = "https://dummyjson.com"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "register_api_data.csv")


def get_test_data():
    data = []
    # 检查文件是否存在
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"测试数据文件不存在，请检查路径：{TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_headers = ["firstName", "lastName", "age", "expect_code", "expect_keyword", "case_desc"]
        if not all(header in reader.fieldnames for header in required_headers):
            raise ValueError(f"CSV文件缺少必要表头，需要包含：{required_headers}")
        #读取每一行测试数据（age转为整数）
        for row in reader:
            data.append((
                row["firstName"],
                row["lastName"],
                int(row["age"]) if row["age"].strip() else None, #处理空age
                int(row["expect_code"]),
                row["expect_keyword"],
                row["case_desc"]
            ))
    return data

@allure.feature("在线接口测试-注册模块")
class TestOnlineRegisterAPI:
    @allure.story("注册接口功能验证")
    @allure.title("{case_desc}")
    @pytest.mark.parametrize("firstName, lastName, age, expect_code, expect_keyword, case_desc", get_test_data())
    def test_register_api(self, firstName, lastName, age, expect_code, expect_keyword, case_desc):
        req_data = {}
        if firstName:
            req_data["firstName"] = firstName
        if lastName:
            req_data["lastName"] = lastName
        if age is not None:
            req_data["age"] = age

        with allure.step("1. 构造注册接口请求"):
            register_url = f"{BASE_API_URL}/users/add"
            headers = {"Content-Type": "application/json"}
            allure.attach(f"请求地址：{register_url}\n请求参数：{req_data}", name="请求信息")

        with allure.step("2. 发送注册接口请求"):
            try:
                #发送POST请求（禁用重定向，避免HTML跳转）
                response = requests.post(
                    url=register_url,
                    json=req_data,
                    headers=headers,
                    timeout=10,
                    allow_redirects=False
                )
                #打印调试信息，方便排查
                print(f"\n【用例】：{case_desc}")
                print(f"【状态码】：{response.status_code}")
                print(f"【响应内容】：{response.json()}")
            except Exception as e:
                pytest.fail(f"接口请求/解析异常：{str(e)}", pytrace=False)

        with allure.step("3. 验证注册接口响应结果"):
            #断言状态码
            assert response.status_code == expect_code, \
                f"状态码断言失败！预期：{expect_code}，实际：{response.status_code}"
            #解析响应JSON
            response_json = response.json()
            #分场景断言响应内容
            if expect_code == 200:
                # 注册成功：必须包含id字段（DummyJSON返回新生成的用户ID）
                assert "id" in response_json, f"注册成功但未返回用户ID！响应：{response_json}"
                # 验证返回的姓名和传入的一致
                assert response_json.get("firstName") == firstName, \
                    f"返回的firstName不匹配！预期：{firstName}，实际：{response_json.get('firstName')}"
                assert response_json.get("lastName") == lastName, \
                    f"返回的lastName不匹配！预期：{lastName}，实际：{response_json.get('lastName')}"
            else:
                # 注册失败：错误信息需包含预期关键词
                assert expect_keyword in response_json.get("message", ""), \
                    f"错误信息断言失败！预期包含：{expect_keyword}，实际：{response_json.get('message', '无错误信息')}"
            # 把响应信息附加到Allure报告
            allure.attach(f"状态码：{response.status_code}\n响应内容：{response_json}", name="响应信息")

# 提示：如需通过终端执行，直接删除下面的注释即可
# if __name__ == "__main__":
#     pytest.main([__file__, "--alluredir", "./allure-results", "-v", "-s"])
#     if os.system("allure --version >nul 2>&1") == 0:
#         os.system(f"allure serve ./allure-results")