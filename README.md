- 仿写项目的部分接口，包括房产接口，开发商接口，开发商下的员工接口，及简单的token登录校验
- 使用python3.6
- 数据库使用mongo+redis缓存
  - 需要在 `config.config.py` 中修改配置
  - 数据库使用`house`
  - 缓存时间为600s，可修改`CACHE_DEFAULT_TIMEOUT`参数
- 可通过`clone`到本地执行 `python manage.py runserver -p 8000 -d -r` 运行
  - 8000是启动的端口
- 也可通过docker进行部署，由于没有把镜像上传到dockerhub，所以也需要将代码`clone`下来
  - 使用了docker-compose进行管理docker(开了两个docker，app+nginx)，请先确保安装了docker-compose
    - 可使用 `docker-compose -v` 查看是否安装成功
    - 安装命令：`pip install docker-compose`
  - docker方式使用gunicorn的gevent启动flask项目
  - clone之后，使用 `docker-compose up -d` 进行后台启动
- 接口说明：
  - 接口目录在`api.__init__.py`文件中
  - 所有参数使用json传参
  - 用户接口：
    - 用户注册：POST：`api/user/register`
      - 参数
       ```
       phone_area   str     手机地区，默认86
       phone        str     手机号，必填
       pwd          str     密码，必填
       name         str     名称，必填
       email        str     邮箱，选填
       icon         str     头像，选填
       nickname     str     昵称，选填

       signature    str     签名，选填
       gender       int     性别，必填 1 男  2 女

       province     str     省份，选填
       city         str     城市，选填
       country      str     国家，选填
       ```
    - 用户登录：POST：`api/user/login`     使用token机制，token有效期1天， 可在config中修改 `EXPIRATION` 参数
      - 参数
        ```
        phone        str    手机号，必填
        pwd          str    密码，必填
        ```
    - 用户详情：GET：`api/user`           需要登录，header头中需要携带token字段
  - 商户接口：
    - 新增商户：POST：`api/merchant`      需要登录，header头中需要携带token字段
      - 参数：
        ```
        name        str     商户名称，选填
        brief       str     商户简介，选填
        logo        str     商户logo，选填
        htype       int     商家类型，必填 1 地产商、2 中介，代理商
        service     int     所需服务，必填 1 推广获客、2 品牌推广

        contacts    str     商户联系人，必填
        phone       str     商户联系手机号，必填
        ```
    - 商户列表：GET：`api/merchant`       需要登录
      - 商户管理员返回所有，不是管理员返回名下商户
    - 具体商户的更新，删除，详情：PUT、DELETE、GET：`api/merchant/<id>`      更新与删除需要登录
      - id为商户id
      - 更新参数参考新增参数，仅需传入需要修改的字段
      - 删除另外检测登录用户是否有此商户的管理员权限
    - 商户审核：PUT：`api/merchant/<id>/examine`      需要登录
      - id为商户id
      - 无需传入参数
      - 该接口将商户审核状态变为已审核，同时新增一个审核时间
    - 获取商户下的房源：GET：`api/merchant/<id>/house`
      - 可另外在url中添加`p`和`s`参数
        - p 参数：第几页，默认第1页
        - s 参数：每页显示几条，默认10条
    - 新增商户员工接口：POST：`api/merchant/<id>/employees`   需要登录
      - 需要检测用户是否是管理员，user表的is_admin字段
      - id为商户id
      - 参数：
        ```
        name        str     员工姓名，必填
        phone       str     员工的手机号，必填
        roles       list[int]    员工级别，必填  1 管理员 2 经纪人
        position    str     员工职位，选填
        logo        str     员工logo，选填
        brief       str     员工简介，选填
        ```
      - 如添加的员工之前未在数据库中，则会新创建一个，初始密码为123456
    - 获取商户下的员工接口：GET：`api/merchant/<id>/employees`      需要登录
      - 需要检测用户是否是管理员，user表的is_admin字段
    - 删除商户员工接口(目前近支持一个个的删除)：DELETE：`api/merchant/<id>/employees`        需要登录
      - 需要检测用户是否是管理员，user表的is_admin字段
      - 参数：
        ```
        user_id     str     员工id，必填
        ```
  - 房源接口：
    - 新增房源：POST：`api/house`     需要登录，且有商户的管理员权限
      - 参数：
        ```
        prices          list    价格，选填
            country     str     货币类型，RMB、USD，选填
            price       float   价格，单位万元，选填
            price_min   float   最低价，选填
            price_max   float   最高价，选填
        addresses       list    地址，选填
            country     str     省，选填
            province    str     市，选填
        merchant_id     int     商户id，必填
        name            str     房源名称，必填
        tags            list[str]    房源标签，选填
        brief           str     房源简介，选填

        category        int     物业类型，必填 1 住宅、2 独栋别墅、3 联排别墅、4 公寓、5 商业房
        sales_status    int     销售状态，必填 1 在售、2 代售

        renovation      int     交房标准，必填 1:毛坯 2:普装 3精装
        build_area      float   建筑面积，选填
        house_hold      int     总户数，选填
        ```
    - 获取房源列表：GET：`api/house`
    - 具体房源的更新，详情，删除：PUT、GET、DELETE：`api/house/<id>`
      - 更新与删除需要登录
      - 删除需要检测用户是否是管理员  user表的is_admin字段
      - 获取列表，可另外在url中添加`p`和`s`参数
        - p 参数：第几页，默认第1页，`?p=2`
        - s 参数：每页显示几条，默认10条, `&s=10`
  - 收藏关注点赞阅读接口：
    - 新增阅读，点赞，关注，收藏接口：POST：`api/action`     需要登录
      - 参数：
        ```
        object_id       str     收藏的对象id，必填
        action_type     int     进行的操作，必填  1 阅读、2 点赞、3 收藏、4 关注
        addition        str     备注信息，选填
        ```
    - 获取用户的关注收藏列表：GET：`api/action`     需要登录
      - 可通过url拼接`a`参数指定查看对应的操作，如`?a=1`则查看用户阅读的记录
    - 删除用户的关注收藏(单个删除)：DELETE：`api/action`     需要登录
      - 可通过url拼接`a`参数选取对应的操作，如`?a=1`则选取用户阅读的记录
      - 参数：
        ```
        object_id       str      对象id，必填
        ```
