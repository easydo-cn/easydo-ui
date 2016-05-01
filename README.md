# easydo-ui
a pythonic UI framewok, no need of dirty javascript &amp; html anymore

革命性前端开发，使用Python来开发web app，不再需要学习了解javascript/html.

## 背景： 为什么前端这么复杂？

当前的前端，没半年基本就会被“轮”一次，新旧更替，开发者叫苦不迭。

一方面投入时间学习的知识没什么价值了，另外一方面，使用旧技术的产品变得没有人才可以去维护。

本质上，现在的浏览器前端技术，并不是为应用开发所准备的，而是为网页渲染。将网页浏览器，改变成应用运行器，这需要标准到工业界的支持。从html5的推出难度就可以看出，这是一个非常慢的过程。

## 梦想： 用python组件化应用开发

既然浏览器进化缓慢，我们可以做一层封装，将网页浏览器变成应用运行器。

我们在后端使用python输出组件，执行应用的渲染和交互:

  from easydo_ui import ui, view
  
  form = ui.form(title="注册", description="在这里完成注册表单")\
            .add(ui.text_line(name="username", title="登录名"))\
            .add(ui.text_line(name="email", title="邮件地址"))\
            .button('register', '注册')\
            .on('submit', submit_url)

  button, errors, result = form.get_submitted(request_form)
  
  if not button:
    return form.html()
  else:
    if errors:
      view.message('errors: %s %s' % errors.items()[0])

使用上面的方法，可以输出一个表单的html代码。

处理这个表单
  
  
