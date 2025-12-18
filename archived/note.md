# 開發中可能遇到的坑


### 解決安裝了 wxpython 后依舊無法 import wx 的問題

C:\Python37\Lib\site-packages\
新增 wx.pth 檔案 內容
wx-3.0-msw


--------



### import win32api 報錯 DLL load failed

嘗試安裝 exe 版本的 pywin32 安裝包

--------

### 解決 Boa-constructor 雙擊后無法打開問題

修改 wx 模組的 __init__.py 檔案 (路徑一般為 C:\Python37\Lib\site-packages\wx-3.0-msw\___init__.py ), 末尾新增一行:
NO_3D = 0


--------



### 解決 boa-constructor 0.6.1 執行原始碼面板中空白一片

在boa根目錄，找到 Palette.py，將 408行的語句 　　　　newButton = btnType(self, mID, None, wx.Point(self.posX, self.posY), 修改爲 　　　　newButton = btnType(self, mID, None, wx.Point(self.posX, 0),
就可以正常使用了

參考：http://blog.csdn.net/rickleo/article/details/6532595


--------



