# 安装依赖
```shell
pip install -r requirements.txt
```
第一次执行可能还需要下载huggingface的embedding model

# 设置OPENAI_API_KEY
该项目使用OPENAI接口，需要`OPENAI_API_KEY`，因此你需要:
1. 新建一个`.env`文件，放在项目根目录下:`react-agent/.env`
1. 在`.env`文件中输入如下配置:
   ```
   OPENAI_API_KEY=你的OPENAI_API_KEY
   ```


# 自定义优化
在`react-agent/customization`文件夹中，有自定义行为的代码。目前自定义修改包括了:
- `pandas_query_engine`在返回查询信息的时候，使用`pd.set_options()`零时的增加返回文本长度（默认返回的每列字符很短，后面会用`...`裁剪）
- `react_agent`的查询模版修改成了中文，不然经产会返回英文的答案

# 使用方法
`python ReactAgent.py` 进入查询模式，默认`verbose = True`以方便调试，案例如下:
```shell
(Datasci) azure@Azures-MacBook-Pro ReactAgent % python ReactAgent.py

==> 问我些大学招生问题:
|->北京工商大学的章程中，录取标准什么
Thought: 我需要使用一个工具来帮助我回答这个问题。
Action: database
Action Input: {'input': '北京工商大学'}
Observation:   北京工商大学  ...  北京工商大学2023年本科招生章程\n                        \n北京工商大学2023年本科招生章程 \n第一章  总则\n第一条 根据《中华人民共和国教育法》、...
[1 rows x 3 columns]
Response: Answer: 北京工商大学的录取标准可以在其章程中找到。根据《北京工商大学2023年本科招生章程》，学校招生工作严格贯彻落实国家教育方针，坚持公平竞争、公正选拔、公开透明的原则，全面考核、综合评价、择优录取，并接受纪检监察部门、考生、家长及社会各界的监督。具体的录取规则和要求可以在章程中找到。
```
