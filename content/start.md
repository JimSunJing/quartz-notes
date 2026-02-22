# 如何用这个东西

以防你忘记了：

```
# 打开powershell
git add -a
git commit -m "new notes update"
git push
```

之后 netlify 会自动抓取 github 推送重新部署

---

本地文件夹有可以将 x 推文/长文保存到 content 的工具
直接运行exe：

- D:\Quartz4\tools\x_url_ingestor\dist\XUrlToQuartz.exe

如果你要源码运行，用这条（从仓库根目录）：

- python tools\x_url_ingestor\run_gui.py
