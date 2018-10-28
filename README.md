# 链家小区成交记录—爬虫
* 本人开发测试环境， win10*64，python3.6.6

### 使用[scrapy](https://scrapy.org/)爬虫框架
* 安装scrapy
    `pip install scrapy`
  > 安装scrapy可以需要安装Twisted,请在这里下载https://pypi.org/project/Twisted/#history或者百度，如https://download.csdn.net/download/taotao223/10018870?web=web
  > 可能需要pywin32，请在这里下载https://github.com/mhammond/pywin32/releases
  > 其他异常自行解决

### 运行
* 运行`lianjia/spiders/lianjia_spider.py`文件里面的__name__方法即可
* 输出csv格式
    需要关闭`settings.py`配置中的ITEM_PIPELINES配置
    ```
    # ITEM_PIPELINES = {
    #    'lianjia.pipelines.LianjiaPipeline': 300,
    # }
    ```
* 输出json格式
    需要开启`settings.py`配置中的ITEM_PIPELINES配置
    ```
    ITEM_PIPELINES = {
       'lianjia.pipelines.LianjiaPipeline': 300,
    }
    ```

### 查询其他区域
* `lianjia_spider.py`默认配置查询白云区
  ```
  start_urls = ['https://gz.lianjia.com/xiaoqu/baiyun/']
  ```
* 更改start_urls查询其他区域，如下为番禺区
  ```
  start_urls = ['https://gz.lianjia.com/chengjiao/panyu/']
  ```
* 可以同时查询多个区域
  ```
  start_urls = ['https://gz.lianjia.com/xiaoqu/baiyun/','https://gz.lianjia.com/chengjiao/panyu/']
  ```
* 查询广州市
  ```
  start_urls = ['https://gz.lianjia.com/chengjiao/']
  ```
* 查询北京市
  ```
  start_urls = ['https://bj.lianjia.com/chengjiao/']
  ```