import torch
print(torch.cuda.is_available())   # 应该输出 True
print(torch.version.cuda)          # 显示你装的 CUDA 版本
print(torch.cuda.get_device_name(0))  # 显示你的显卡名称
