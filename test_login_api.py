# -*- coding: utf-8 -*-
# @Time    : 2021/8/14 23:46
# @Author  : Flora.Chen
# @File    : test_login_ui.py
# @Software: PyCharm
# @Desc:

from test_api import os, API_DATA, BaseApi, json, pytest, operate_deepdiff, logger, EnvData, extras
from utils.otherUtils.handle_eval_data import eval_data_process


def check_case_data():
    data = EnvData.check_data(os.path.join(API_DATA, "login_data.yaml"))
    return data


@pytest.mark.api
@pytest.mark.loginapi
class TestLoginApi:
    """
    登录的API测试用例
    """

    cases = check_case_data()
    logger.debug("测试一下这部分代码是否运行")

    @pytest.mark.parametrize("case", cases, ids=["{}".format(case["title"]) for case in cases])
    def test_login_api(self, case, env_users, extra):
        """
       测试登录接口的测试用例
        """

        if case["is_run"] is False:
            reason = f"该用例：[{case['title']}], 用例文件设置了暂时跳过， is_run=false"
            logger.info(reason)
            pytest.skip(reason)

        logger.info("--------------开始执行用例--------------")
        logger.info(f"用例标题：{case['title']}")
        logger.info(f"初始用例数据：{case}")
        host, users = env_users

        # 给测试数据类设置类属性，方便后面用例数据的替换
        setattr(EnvData, "login", users["reporter"]["user"])
        setattr(EnvData, "password", users["reporter"]["pwd"])
        setattr(EnvData, "username", users["reporter"]["nickname"])
        setattr(EnvData, "user_id", users["reporter"]["id"])

        # 替换用例数据
        case = EnvData.replace_data(json.dumps(case, ensure_ascii=False))
        case = json.loads(case)
        case["url"] = host + case["url"]
        logger.info(f"替换后的用例数据：{case}")
        extra.append(extras.text(str(case), name="替换后的用例数据"))

        # 断言
        try:
            response = BaseApi().send_request(**case)
            actual = response.json()
            expected = eval_data_process(case['assert']['expected_response'])
            logger.info(f"预期结果：{expected}\n实际结果：{actual}")
            extra.append(extras.text(f"预期结果：{expected}\n实际结果：{actual}", name="测试结果"))
            if case["assert"].get("expected_response_code"):
                assert response.status_code == case["assert"]["expected_response_code"]

            if case["assert"].get("expected_response"):
                operate_deepdiff(case["assert"]["expected_response"], actual,
                                 {"exclude_paths": {"root['image_url']", "root['is_watch']", "root['admin']",
                                                    "root['user_identity']"}})
        except AttributeError as e:
            logger.error(f"断言时遇到了异常：{e}，当前用例：【{case['title']}】测试失败")
            raise e
        else:
            logger.info(f"当前用例：【{case['title']}】测试通过")
        finally:
            logger.info("--------------当前用例执行完毕--------------")
