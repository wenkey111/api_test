# api_test
接口自动化测试项目（实习用）

一、项目简介

本项目基于Python + Pytest + Requests + Allure实现电商接口自动化测试，针对开源接口网站（Fake Store API/Dummy JSON）完成基本场景覆盖，并完整落地GitHub Actions CI流程，实现「代码提交→自动测试」全自动化。

二、技术栈

Python、Requests、Pytest、Allure、CSV数据驱动、CI持续集成；

三、CI说明

本项目已配置GitHub Actions自动化流程，触发规则：

自动触发：代码推送到main分支时，自动执行测试流程；

手动触发：在GitHub仓库「Actions」标签页，点击「Run workflow」手动执行；

四、CD说明

我理解的CD就是测试通过后自动部署，比如接口测试通过后，系统会自动把后端代码部署到预发布环境，等预发布环境的验证通过后，就会自动部署到生成环境（上线）。
