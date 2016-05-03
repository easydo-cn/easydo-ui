# easydo-ui
a pythonic UI framewok, no need of dirty javascript &amp; html anymore

革命性前端开发，使用Python来开发web app，不再需要学习了解javascript/html.

## 背景： 为什么前端这么复杂？

当前的前端，没半年基本就会被“轮”一次，新旧更替，开发者叫苦不迭。

一方面投入时间学习的知识没什么价值了，另外一方面，使用旧技术的产品变得没有人才可以去维护。

本质上，现在的浏览器前端技术，并不是为应用开发所准备的，而是为网页渲染。将网页浏览器，改变成应用运行器，这需要标准到工业界的支持。从html5的推出难度就可以看出，这是一个非常慢的过程。

## 梦想： 用python组件化应用开发

既然浏览器进化缓慢，我们可以做一层封装，将网页浏览器变成应用运行器。

我们在后端使用python输出组件，执行应用的渲染和交互.

理解ui、view、应用运行器:
  
- ui是组件界面库，用来生成html的；
- view是应用运行器的控制器，用来生成javascript的；
- 所谓应用运行器，是在浏览器上运行的初始页面，这个页面可以接受后端返回的view指令；


下面输出一个表单html::

    from easydo_ui import ui
    form = ui.form(title="注册", description="在这里完成注册表单")\
              .add(ui.text_line(name="username", title="登录名"))\
              .add(ui.text_line(name="email", title="邮件地址"))\
              .button('register', '注册')\
              .on('submit', submit_url)
    return form.html()

如果在模板主区域ajax显示::

    view.layout.main().set_content(form)
    return view.javascript()

如果需要遮罩方式弹出显示:

    from easydo_ui import ui, Commands
    view = Commands()
    view.modal(form)
    return view.javascript()

如果需要处理表单:

    button, errors, result = form.get_submitted(request_form)
    if errors:
        view.message('errors: %s %s' % errors.items()[0])
    else:
        # TODO: process result
        view.message('saved')
    return view.javascript()

## ui组件库

类似bootstrap，easydo-ui提供了一组界面组件：

    ui.h1
    ui.text
    ui.paragraph
    ui.link
    ui.button
    ui.button_group
    ui.tree
    ui.tabs
    ui.list_group
    ui.panel

## view指令

常见的view指令包括:

    view.message
    view.modal
    view.close_modal()
    view.find
    view.select
    view.closest
    view.on
    view.trigger

## 应用运行器

应用运行器需要加载 easydo-ui.js. 

也可以在javascript中，直接向后端发起一个ajax调用，方法为：

    TODO

## 扩展组件

如果需要扩展一个新的ui组件，可以 @ui_component 修饰器来定义:

    form easydo_ui import component_ui, component_commands, BaseCommands

    @component_ui
    class mytree(BaseElement):

        def html(self):
            result = ''
            # TODO render as html
            return result

    @component_commands('mytree')
    class mytree_commands(BaseCommands):

        def expand(self):
            pass

一旦定义，可以如下引用:

    ui.mytree()
    view.find('mytree').expand()
