# encoding: utf-8
import cgi, os
import json
import random
import urlparse
from types import StringTypes
from tempfile import NamedTemporaryFile
from commands import component_commands

from zopen.kssaddons.kss import KssCommands
from zopen.navtree.api import render_navtree


class BaseUI:

    def __add__(self, widget):
       return CompositeUI(self, widget)

    def __str__(self):
        return self.html()

class BaseKss:
    name = ''
    selector = ''

    def __init__(self, kss):
        self.kss = kss

    def set_content(self, content='', js_var=None):
        self.kss.set_content(content, js_var)

    def append(self, content):
        self.kss.append(content)

    def prepend(self, content):
        self.kss.prepend(content)

    def brefore(self, content):
        self.kss.before(content)

    def after(self, content):
        self.kss.after(content)

    def empty(self):
        self.kss.empty()

    def off(self, event):
        self.kss.remove_class('kss')
        return self

    def trigger(self, event_name, data):
        self.kss.trigger(event_name, data)
        return self

    def find(self, selector):
        self.kss.find(selector)
        return self

    def children(self, selector):
        self.kss.children(selector)
        return self

    def filter(self, selector):
        self.kss.filter(selector)
        return self

    def exclude(self, selector):
        self.kss.exclude(selector)
        return self

class CompositeUI(BaseUI):

    def __init__(self, a, b):
        self.uis = [a, b]

    def __add__(self, widget):
        self.uis.append(widget)
        return self

    def html(self):
        return ''.join([item.html() for item in self.uis])

class Element(BaseUI):
    el = ''
    _icon = ''
    _klass = ['kss-com']
    drop_menu = None
    drop_dir = 'down'
    id = ''

    def __init__(self, title='', id='', klass='', **attr):
        self.data = {}
        self.title = title
        self.attr = attr
        self.klass = list(self._klass)
        self.children = []
        self._triggers = {}
        self._off = []

        self.id = id
        if klass:
            self.klass.append(klass)

    def icon(self, name, **kw):
        classes = 'fa fa-%s' % name
        for key, value in kw.items():
            if key == 'size':
                classes += ' da-%s' % value
            elif key in ('rotate', 'flip'):
                classes += ' da-%s-%s' % (key, value)
            elif key == 'pull':
                classes += ' pull-%s' % value
            elif key in ('spin', 'muted', 'border') and value is True:
                classes += ' fa-%s' % key
        self._icon = '<i class="%s"></i> ' % classes
        return self

    def on(self, event, kss, func=''):
        if event in ('click', 'submit'):
            self.klass.append('kss')
            self.data['kss'] = kss
            if event == 'submit' and not hasattr(self, 'form_def'):
                self.klass.append('kss-form')
        elif event == 'drop' and not getattr(self, '_dnd', None):
            self.klass.append('kss-droppable')
            self.data['drop'] = kss
        elif event == 'expand':
            self.data['expand'] = kss

        self._triggers.setdefault(event, []).append((kss, func))
        return self

    def off(self, event):
        self._off.append(event)
        return self

    def add(self, child):
        self.children.append(child)
        return self
    child = add

    def dropdown(self, menu):
        self.drop_menu = menu
        self.drop_dir = 'down'
        return self

    def dropup(self, menu):
        self.drop_menu = menu
        self.drop_dir = 'up'
        return self

    def draggable(self, data={}):
        self.klass.append('kss-draggable')
        self.data['drag'] = cgi.escape(json.dumps(data), True)
        return self

    def html(self):
        if 'loading' in self.data:
            self.klass.append('KSSLoad')

        arrow = ''
        if self.drop_menu is not None and self.drop_dir == 'down':
            self.klass.append('arrow_down')
            arrow = '<span class="bgicon">&nbsp;&nbsp;&nbsp;</span>'

        attr = self.attr.items()
        if self.id:
            attr.append(('id', self.id))
        attr.append(('class', ' '.join(self.klass)))

        attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in attr])
        data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in self.data.items()])
        children = ''.join([child.html() for child in self.children])

        _html = '<%s %s %s>%s%s%s %s</%s>' % \
                (self.el, attr, data, self._icon, self.title, children, arrow, self.el)

        if self.drop_menu is not None:
            drop = self.drop_menu.html()
            if self.drop_dir == 'up':
                return '<dl class="actionMenu relative"> \
                    <dd class="actionMenuContent KSSActionMenuContent hidden">%s</dd> \
                    <dt class="KSSActionMenu" onclick="var prev = $(this).prev();window.setTimeout(function(){prev.css(&quot;top&quot;,0-prev.height())},10);">%s</dt></dl>' % (drop, _html)
            else:
                return '<dl class="actionMenu" style="display: inline-block;"><dt class="KSSActionMenu">%s</dt> \
                    <dd class="actionMenuContent KSSActionMenuContent hidden">%s</dd></dl>' % (_html, drop)
        else:
            return _html

class script(Element):
    el = 'script'

    def __init__(self):
        Element.__init__(self)
        self.kss = KssCommands(None, None)

    def on(self, event, kss, conditions={}):
         self.kss.on(event, kss, conditions)
         return self

    def off(self, event, kss=''):
         self.kss.off(event, kss)
         return self

    def html(self):
        return '<script type="text/javascript">$(function(){%s});</script>' % self.kss.generate_js()

class h1(Element):
    el = 'h1'

class h2(Element):
    el = 'h2'

class h3(Element):
    el = 'h3'

class h4(Element):
    el = 'h4'

class h5(Element):
    el = 'h5'

class image(Element):
    el = 'image'

class link(Element):
    el = 'a'

    def __init__(self, title='', href='#', **attr):
        Element.__init__(self, title=title, href=href, **attr)

    def kss(self, kss_url):
        self.on('click', kss_url)
        return self

    def loading(self, text, layout=None):
        self.data['loading'] = text
        return self

    def active(self):
        self.klass.append('selected')
        return self

    def button(self):
        self.klass.append('button')
        return self

    def danger(self):
        self.klass.append('danger')
        return self

    def primary(self):
        self.klass.append('primary')
        return self

    def flat(self):
        self.klass.append('minor')
        return self

    def disable(self):
        self.klass.append('disable')
        return self

class button(link):
    el = 'button'
    _klass = ['button']

    def __init__(self, title='', **attr):
        Element.__init__(self, title=title, **attr)

    def active(self):
        self.klass.append('active')
        return self

    def pill(self):
        self.klass.append('pill')
        return self

    def size(self, num):
        if num == 'large':
            self.klass.append('btn-lg')
        elif num == 'small':
            self.klass.append('btn-xl')
        elif num == 'xsmall':
            self.klass.append('btn-xs')
        return self

class text(Element):
    el = 'span'
    _text = ''

    def __init__(self, text='', **attr):
        Element.__init__(self, **attr)
        self._text = text

    def html(self):
        if self.el == 'p':
            self.title = self._text.replace('\n', '<br>')
        else:
            self.title = self._text
        return Element.html(self)

    def discreet(self):
        self.klass.append('discreet')
        return self

class paragraph(text):
    el = 'p'

class badge(text):
    _klass = ['badge']

class pre(text):
    el = 'pre'

    def __init__(self, title='', **attr):
        title = cgi.escape(title)
        text.__init__(self, title, **attr)

class div(Element):
    el = 'div'

class raw(Element):
    _html = ''

    def __init__(self, html='', **attr):
        Element.__init__(self, **attr)
        self._html = html

    def html(self):
        return self._html

class html(Element):
    _html = ''

    def __init__(self, html, **attr):
        Element.__init__(self, **attr)
        self._html = html

    def html(self):
        attr = self.attr.items()
        if self.id:
            attr.append(('id', self.id))

        self.klass.append('html')
        attr.append(('class', ' '.join(self.klass)))

        attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in attr])
        data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in self.data.items()])

        return '<div %s %s>%s</div>' % (attr, data, self._html)

@component
class panel(Element):

    def __init__(self, *arg, **attr):
        Element.__init__(self, **attr)
        for _widget in arg:
            self.add(_widget)

        self._kss = ''
        self._title = ''
        self._footer = ''
        self._collapse = None
        self._toolbox = ''

    def html(self):
        content = ''
        for child in self.children:
            content += child.html()

        if 'expand' in self._triggers:
            self._kss = self._triggers['expand'][0][0]
            self._collapse = False

        attr = self.attr.items()
        if self.id:
            attr.append(('id', self.id))

        classes = ' '.join(self.klass)
        attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in attr])
        data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in self.data.items()])

        if not self._title and not self._toolbox:
            return '<div class="panel %s" %s %s><div class="panel-body">%s</div></div>' % (classes, attr, data, content)

        if self._collapse is not None or self._kss:
            _collapse_hide = self._collapse and 'hidden' or ' '
            _collapse_show = self._collapse and ' ' or 'hidden'

            if self._kss:
                head = '''
                    <span class="KSSShowHideTarget hidden">
                        <span class="rightwardDelta KSSShowHideTarget"><!-- --></span> %s
                    </span>
                    <span class="kss KSSAjaxLoad KSSShowHideTarget" data-kss="%s">
                        <span class="rightwardDelta KSSShowHideTarget"><!-- --></span> %s
                    </span> ''' % (self._title, self._kss, self._title)
            else:
                head = '''<span class="rightwardDelta KSSShowHideTarget %s"><!-- --></span>%s''' % (_collapse_hide, self._title)

            html = '''
            <div id="%s" class="panel %s KSSShowHideArea" %s %s>
                <div class="panel-heading">
                    <div class="panel-toolbox">%s</div>
                    <div class="panel-heading-content">
                        <span class="KSSShowHideAction">
                            <span class="downwardDelta KSSShowHideTarget %s"><!-- --></span>
                            %s
                        </span>
                    </div>
                </div>
                <div class="panel-body KSSShowHideTarget %s %s" %s>%s</div>
                %s
            </div>
            ''' % (self.id,
                   classes,
                   attr,
                   data,
                   self._toolbox,
                   _collapse_show,
                   head,
                   _collapse_show,
                   classes,
                   data,
                   content,
                   self._footer and ('<div class="panel-footer KSSShowHideTarget %s">%s</div>' % \
                   (_collapse_show, self._footer)) or ''
                   )
            return html
        else:
            html = '''
            <div id="%s" class="panel %s" %s %s>
                <div class="panel-heading">
                    <div class="panel-toolbox">%s</div>
                    <div class="panel-heading-content">%s</div>
                </div>
                <div class="panel-body">%s</div>
                %s
            </div>
            ''' % (self.id,
                   classes,
                   attr,
                   data,
                   self._toolbox,
                   self._title,
                   content,
                   self._footer and ('<div class="panel-footer">%s</div>' % self._footer) or ''
                   )
            return html

    def collapse(self, default=True):
        self._collapse = default
        return self

    def loading(self, text):
        self.data['loading'] = text
        return self

    def header(self, element):
        if isinstance(element, basestring):
            self._title = element
        else:
            self._title = element.html()
        return self
    title = header
    head = header

    def footer(self, element):
        if isinstance(element, basestring):
            self._footer = element
        else:
            self._footer = element.html()
        return self

    def toolbox(self, element):
        if isinstance(element, basestring):
            self._toolbox = element
        else:
            self._toolbox = element.html()
        return self

    @command
    def panel_body(self):
        if self.kss._selector.startswith('$(NODE)'):
            self.kss.find('.panel-body').remove_class('hidden')
            self.kss.closest('.panel').find('.panel-body')
        else:
            self.kss.find('.panel-body')
        return self

class layout(Element):
    _direction = 'horizontal'

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        for _widget in arg:
            self.add(_widget)

    def horizontal(self):
        self._direction = 'horizontal'
        return self

    def vertical(self):
        self._direction = 'vertical'
        return self

    def html(self):
        attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in self.attr.items()])
        if self._direction == 'horizontal':
            cols = []
            for child in self.children:
                if hasattr(child, 'width') and child.width:
                    classes = 'span%d' % child.width
                else:
                    classes = ''
                cols.append('<div class="%s">%s</div>' % (classes, child.html()))
            content = '<div id="%s" class="%s layout row-fluid" %s>%s</div>' \
                           % (self.id, ' '.join(self.klass), attr,  ''.join(cols))
        else:
            rows = []
            for child in self.children:
                rows.append('<div class="layout-block">%s</div>' % child.html())
            content = '<div id="%s" class="%s layout layout-vertical" %s>%s</div>'\
                           % (self.id, ' '.join(self.klass), attr, ''.join(rows))
        return content

    def add(self, widget, width=0):
        widget.width = width
        self.child(widget)
        return self

class list_group(Element):

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        self.children = []
        for _widget in arg:
            self.children.append(_widget)

    def html(self):
        content = '<ul id="%s" class="list-group %s">' % (self.id, ' '.join(self.klass))
        for link in self.children:
            if 'selected' in link.klass:
                classes = 'list-group-item navTreeItem selected'
            else:
                classes = 'list-group-item navTreeItem'
            content += '<li class="%s">%s</li>' % (classes, link.html())
        content += '</ul>'
        return content

class button_group(Element):

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        self.children = []
        for _widget in arg:
            self.children.append(_widget)

    def html(self):
        return '<div id="%s" class="%s button-group">%s</div>'\
                 % (self.id, ' '.join(self.klass), ''.join([x.html() for x in self.children]))

class nav(Element):

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        self.children = []
        for _widget in arg:
            self.children.append(_widget)

    def html(self):
        return '<nav id="%s" class="%s"><ul>%s</ul></nav>'\
                   % (self.id, ' '.join(self.klass), ''.join(['<li>%s</li>' % x.html() for x in self.children]))

class grid(Element):

    def __init__(self, rows, columns, **kw):
        Element.__init__(self, **kw)
        self.cells = []
        self.headers= ['' for i in range(columns)]
        for i in range(rows):
            self.cells.append(['' for i in range(columns)])
        self._dnd = False

    def dnd(self):
        self._dnd = True
        if not self.id:
            self.id = 'grid-%d' % random.randrange(0, 9999)
        return self

    def set(self, row, col, widget):
        if isinstance(widget, BaseUI):
            widget = widget.html()
        self.cells[row][col] = widget
        return self

    def set_header(self, col, widget):
        if isinstance(widget, BaseUI):
            widget = widget.html()
        self.headers[col] = widget
        return self

    def html(self):
        rows = []
        has_header = ''.join(self.headers)
        if has_header:
            headers = []
            for header in self.headers:
                headers.append('<th>%s</th>' % header)
            header = '<thead><tr class="nodrop nodrag">%s</tr></thead>' % ''.join(headers)
        else:
            header = ''
        for index, row in enumerate(self.cells):
            cols = []
            for col in row:
                cols.append('<td>%s</td>' % col)
            rows.append('<tr id="%s-%d">' % (self.id, index) + ''.join(cols) + '</tr>')

        data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in self.data.items()])
        html = '<table id="%s" class="%s listing" %s>%s<tbody>%s</tbody></table>' %\
               (self.id , ' '.join(self.klass), data, header, ''.join(rows))

        on_drop = self._triggers.get('drop', [])
        if self._dnd and on_drop:
            html += """<script type="text/javascript">
    load(['jquery.tablednd.js'], function(){
        $("#%(grid_id)s dl, #%(grid_id)s dt").css('display', 'inline');
        $("#%(grid_id)s").tableDnD({
            onDragStart:function (table, row){
                var rows = $(table).find("tbody:first>tr");
                var index = 0;
                for (var i = 0; i<rows.length; i++){ if (row == rows[i]){ index = i; } }
                $(row).attr("_index", index);
                },
            onDrop:function (table, row){
                var rows = $(table).find("tbody:first>tr");
                var index = 0;
                for (var i = 0; i<rows.length; i++){ if (row == rows[i]){ index = i; } }
                $(row).kss("%(on_drop)s", {'from':$(row).attr("_index") , 'to':index}, 'GET');
                }
            });
    });</script>
""" % {'grid_id':self.id, 'on_drop':on_drop[0][0]}
        return html

class menu(Element):

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        self.items = []
        for link in arg:
            if isinstance(link, seperator):
                title = None
            else:
                title = link.title

            submit_event = link._triggers.get('submit', [])
            event = link._triggers.get('click', []) or submit_event
            if event:
                kss = event[0][0]
            else:
                kss = ''
            klass= submit_event and 'kss-form' or ''
            self.items.append((title, link.attr.get('url', '#'), kss, klass, False))

    def append(self, title, url='#', kss='', klass='', disabled=False):
        self.items.append((title, url, kss, klass, disabled))
        return self

    def html(self):
        items = []
        for title, url, kss, klass, disabled in self.items:
            if title is None:
                items.append('<li class="seperator"></li>')
                continue
            if kss:
                items.append('<li><a class="kss %s" data-kss="%s" href="%s">%s</a></li>' % (klass, kss, url, title))
            else:
                items.append('<li><a href="%s">%s</a></li>' % (url, title))
        return '<ul id="%s" class="%s">%s</ul>' % (self.id, ' '.join(self.klass), ''.join(items))

class seperator(Element):
    pass

class tabs(Element):

    def __init__(self, **kw):
        Element.__init__(self, **kw)
        self.children = []
        self._has_selected = False

    def tab(self, link, panel, id=''):
        if not id:
            id = 'tab-%d' % (len(self.children) + 1)

        selected = 'selected' in link.klass
        if not self._has_selected:
           self._has_selected = selected

        link.klass.append('node')
        link.classes = selected and 'selected' or ''
        panel.classes = selected and 'tabBody' or 'tabBody hidden'

        self.children.append((link, panel, id))
        return self

    def html(self):
        header = '<ul class="tabs">'
        content = ''
        for index, (_link, _panel, _id) in enumerate(self.children):
            if not self._has_selected and index == 0:
                _link.classes = 'selected'
                _panel.classes = 'tabBody'
            _link.attr['href'] = '#tab-%d-%d' % (id(self), index)
            header += '<li class="%s" id="%s">%s</li>' % (_link.classes, _id, _link.html())
            content += '<div id="%s" class="%s">%s</div>' % (_link.attr['href'][1:], _panel.classes, _panel.html())
        header += '</ul>'
        return '<div id="%s" class="%s tabArea">%s<div class="visualClear"><!-- --></div>%s</div>' \
                     % (self.id, ' '.join(self.klass), header, content)

@component_commands
class KssTabs(BaseKss):
    name = 'tabs'
    selector = '.tabArea'

    def active_panel(self):
        self.kss.children('.tabBody').exclude('.hidden')
        return self

    def toggle_active(self, id):
        self.kss.find('.tabs li#%s a' % id).trigger('click')

    def remove_tab(self, id):
        self.toggle_active(id)
        self.active_panel().remove()
        self.kss.find('.tabs li#%s').remove()

    def add_tab(self, link, panel, id=''):
        if not id:
            id = 'tab-%s' % random.randrange(0, 9999)
        else:
            id = 'tab-%s' % id

        link.klass.append('node')
        link.attr['href'] = '#%s-%s' % (id, random.randrange(0, 9999))
        tab = '<li id="tab-%s">%s</li>' % (id, link.html())

        self.kss._append_script("%s.find('.tabs').append(%s)" % (self.kss._selector, self.kss._escape_value(tab)), False, False)
        self.kss.append('<div id="%s" class="tabBody hidden">%s</div>' % (link.attr['href'][1:], panel.html()))


@component_commands
class KssLayout(BaseKss):

    def main(self):
        self.kss.select('#content')
        return self

    def left(self):
        self.kss.select('#columns').add_class('leftcol')
        self.kss.select('#left .visualPadding')
        return self

    def right(self):
        self.kss.select('#columns').add_class('rightcol')
        self.kss.select('#right .visualPadding')
        return self

    def above(self):
        self.kss.select('#viewlet-above-content')
        return self

    def top(self):
        self.kss.select('#top')
        return self

    def hide_right(self):
        self.kss.select('#columns').remove_class('rightcol')
        return self.kss.select('#right').add_class('hidden')

    def hide_left(self):
        self.kss.select('#columns').remove_class('leftcol')
        return self.kss.select('#left').add_class('hidden')

    def show_right(self):
        self.kss.select('#columns').add_class('rightcol')
        return self.kss.select('#right').remove_class('hidden')

    def show_left(self):
        self.kss.select('#columns').add_class('leftcol')
        return self.kss.select('#left').remove_class('hidden')

class KssCookie(BaseKss):

    def set(self, name, value, expires=36500, path='/'):
        return self.kss.set_cookie(name, value, expires, path)

    def remove(self, name, path='/'):
        return self.kss.remove_cookie(name, path)

class KssBatchActions(BaseKss):

    def close(self):
        return self.kss.close_batch_actions()

    def set_content(self, content):
        return self.kss.set_batch_actions(content)

class History(BaseKss):

    def push_state(self, request, title, url=''):
        return self.kss.push_state(request, title, url)

    def go(self, step):
        return self.kss.go(step)

KssCommands.history = property(History)
KssCommands.layout = property(KssLayout)
KssCommands.cookie = property(KssCookie)
KssCommands.batch_actions = property(KssBatchActions)
KssCommands.assistant = property(Assistant)
KssCommands.rtc = property(KssMessage)

class tree(Element):

    def __init__(self, *arg, **kw):
        Element.__init__(self, **kw)
        self._expand = False
        self.children = []
        for _widget in arg:
            self.children.append(_widget)

    def expand(self):
        self._expand = True
        return self

    def _get_items(self, children):
        items = []
        for child in children:
            if child.id: child.attr['id'] = child.id
            child.attr['class'] = ' '.join(child.klass)
            attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in child.attr.items()])
            data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in child.data.items()])
            item = {
                'icon': child._icon,
                'classes': 'navTreeItem',
                'title': child.title,
                'data': data,
                'attr': attr,
                'expanded': self._expand and 'expand' not in child.data,
            }
            if child.children:
                item['children'] = self._get_items(child.children)
            elif 'expand' not in child.data:
                item['children'] = None
            items.append(item)
        return items

    def html(self):
        template = '<a {{{data}}} {{{attr}}}>{{{icon}}}{{title}}</a>'
        return '<div id="%s" class="ui-tree %s">%s</div>' % \
            (self.id, ' '.join(self.klass),
             render_navtree(self._get_items(self.children), template))

class KssTree(BaseKss):
    name = 'tree'
    selector = '.ui-tree'

    def _get_items(self, children):
        items = []
        for child in children:
            if child.id: child.attr['id'] = child.id
            child.attr['class'] = ' '.join(child.klass)
            attr = ' '.join(['%s="%s"' % (name, value) for (name, value) in child.attr.items()])
            data = ' '.join(['data-%s="%s"' % (name, value) for (name, value) in child.data.items()])
            item = {
                'icon': child._icon,
                'classes': 'navTreeItem',
                'title': child.title,
                'data': data,
                'attr': attr,
            }
            if child.children:
                item['children'] = self._get_items(child.children)
            elif 'expand' not in child.data:
                item['children'] = None
            items.append(item)
        return items

    def add_child(self, id, *links):
        template = '<a {{{data}}} {{{attr}}}>{{{icon}}}{{title}}</a>'
        html = '%s' % render_navtree(self._get_items(links), template, True)
        self.kss.find('#%s' % id).parent().append(html)
        self.kss.remove_class('loadTree')
        return self

KssCommands.register_component(KssTree)

class graph(Element):

    def __init__(self, rankdir="UD", **kw):
        Element.__init__(self, **kw)
        self.dots = []
        self.DOT_SET = '''
rankdir = %s;
nodesep = 0.5;
node [fontname = "monospace",fontsize = 12];
edge [fontname = "monospace",fontsize = 12];
''' % rankdir

    def _escape(self, data):
        return ', '.join(['%s="%s"' % (key, cgi.escape(value, True)) for key, value in data.items()])

    def node(self, name, label=None, url='', shape='box', color='black', tooltip='', **kw):
        if label is None: label = name
        kw.update({'label':label, 'tooltip':tooltip})
        self.dots.append('%s [shape="%s", color="%s", fontsize="14", URL="%s", %s]' % \
             (name, shape, color, url, self._escape(kw)))
        return self

    def edge(self, start, end, label='', url='', color='black', style='bold', **kw):
        self.dots.append('%s -> %s [color="%s", style="%s", URL="%s",%s%s];' % \
            (start, end, color, style, url, self._escape({'label':label}), self._escape(kw)))
        return self

    def subgraph(self, name, nodes, title='', url='', style='dotted', color='black'):
        self.dots.append('subgraph cluster_%s{ label="%s"; URL="%s";style="%s";color="%s";%s }'\
            % (name, cgi.escape(title, True), url, style, color, '\n'.join(nodes)))
        return self

    def dot2graph(self, dot, format='svg'):
        # windows 下临时文件必须先关闭才能被其他程序使用
        # 因此不能使用 NamedTemporaryFile 的自动删除
        with NamedTemporaryFile(delete=False) as dotfile:
            dotfile.write(dot)
        outfile = NamedTemporaryFile(delete=False)
        os.system('dot -Efontname=sans -Nfontname=sans %s -o%s -T%s' % (
            dotfile.name, outfile.name, format))
        result = outfile.read()
        outfile.close()
        os.unlink(dotfile.name)
        os.unlink(outfile.name)
        return result

    def html(self):
        source = '''digraph { %s %s}''' % (self.DOT_SET, '\n'.join(self.dots))
        return """<div id="%s" class="ui-graph %s">%s</div>
<script>
$( function(){
var view_edit_from = function(){
            var url=$(this).attr('xlink:href');
            $(this).kss(url);
            return false;}

$('div.ui-graph .node a').click(view_edit_from)
            .mouseover(function(){$(this).find('polygon').attr('fill', '#79A7D9');})
            .mouseleave(function(){$(this).find('polygon').attr('fill', 'none');})

$('div.ui-graph .edge a').click(view_edit_from)
} )
</script>""" % \
                (self.id, ' '.join(self.klass), self.dot2graph(source))

from . import message
message  # evaluate one time to get rid of flake8 unused import warning

