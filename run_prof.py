# run_prof.py
import cProfile
import backend.app   # 或者你的入口模块

if __name__ == "__main__":
    # 假设你的 FastAPI 在 app.py 里, 这里用一个简单调用示例
    # 如果你有测试脚本，就调用测试脚本
    def main():
        # 例如手动调用部分函数，或用 requests 发送几个 HTTP 请求
        from backend.app import driver, app
        # … 自己写点模拟调用，或者直接启动 app……
        pass

    cProfile.run('main()', filename='profile.prof')
