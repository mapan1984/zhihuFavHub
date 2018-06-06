## 目的

当我们在知乎关注了多个同类型的收藏夹之后，浏览时要一个一个地翻收藏夹，而且多个同类型的收藏夹一般会有大量的重复内容。所以为了更加方便的浏览知乎收藏，可以定时将多个同类型收藏夹的新增内容合并到一个单独的收藏夹中，并且去除重复的内容。

## 使用

修改`config.json`文件的`favlist_id`为你创建的聚合收藏夹id，`collection_ids`为要聚合的收藏夹id列表。

``` json
{
    "favlist_id": "22510446",
    "collection_ids": [
        "45767396",
        "40140271",
        "29475875",
        "53766495",
        "29715631"
    ]
}
```

导出浏览器的cookie(Mozila格式)保存到`cookie.txt`文件中。

运行`client.py`。

## 定时运行

我利用systemd完成定时运行，首先创建服务，在`/usr/lib/systemd/system`中新建文件`zhihub.service`，内容如下：

``` txt
[Unit]
Description=zhihu favlist hub

[Service]
ExecStart=/bin/python3 /path/to/client.py
```

启动/查看状态/关闭服务：

    $ sudo systemctl start zhihub.service
    $ sudo systemctl status zhihub.service
    $ sudo systemctl stop zhihub.service

然后创建定时器，在`/usr/lib/systemd/system`中新建文件`zhihub.timer`，内容如下：

``` txt
[Unit]
Description=zhihu favlist hub

[Timer]
//OnUnitActiveSec=6h
OnUnitActiveSec=*-*-* 05:00:00
Unit=zhihub.service

[Install]
WantedBy=multi-user.target
```

启动/查看状态/关闭定时器：

    $ sudo systemctl start zhihub.timer
    $ sudo systemctl status zhihub.timer
    $ sudo systemctl stop zhihub.timer

设置/关闭开机自启：

    $ sudo systemctl enable zhihub.timer
    $ sudo systemctl disable zhihub.timer
